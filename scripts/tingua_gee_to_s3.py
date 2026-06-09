"""
SISTEMA TINGUA — Automatizacion GEE → S3
Descarga CSVs de Google Drive y los sube a S3
Uso: python scripts/tingua_gee_to_s3.py
"""

import boto3
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configuracion
S3_BUCKET = 'data-pipeline-rob-2026'
S3_PREFIX = 'tingua/gee/'
DRIVE_FOLDER = 'TINGUA'
REGION = 'us-east-2'

# Archivos a sincronizar
ARCHIVOS_GEE = [
    'tingua_ndwi_cienaga_grande.csv',
    'tingua_ndwi_mallorquin_totumo.csv',
    'tingua_ndvi_ndwi_3humedales.csv'
]

def get_drive_service():
    """Autenticacion Google Drive via credenciales de servicio"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def find_file_in_drive(service, filename, folder_name='TINGUA'):
    """Busca un archivo en Google Drive por nombre"""
    query = f"name='{filename}' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    files = results.get('files', [])
    return files[0] if files else None

def download_from_drive(service, file_id, filename):
    """Descarga un archivo de Google Drive"""
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    print(f'  Descargado: {filename}')
    return buffer

def upload_to_s3(buffer, filename):
    """Sube archivo a S3"""
    s3 = boto3.client('s3', region_name=REGION)
    key = f"{S3_PREFIX}{filename}"
    s3.upload_fileobj(buffer, S3_BUCKET, key)
    print(f'  Subido a S3: s3://{S3_BUCKET}/{key}')

def main():
    print(f'=== TINGUA GEE→S3 Sync ===')
    print(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print()
    
    # Conectar a Google Drive
    print('Conectando a Google Drive...')
    service = get_drive_service()
    
    # Sincronizar cada archivo
    for filename in ARCHIVOS_GEE:
        print(f'Procesando: {filename}')
        file_info = find_file_in_drive(service, filename)
        
        if file_info:
            buffer = download_from_drive(service, file_info['id'], filename)
            upload_to_s3(buffer, filename)
            print(f'  OK - {file_info["modifiedTime"]}')
        else:
            print(f'  SKIP - No encontrado en Drive')
        print()
    
    print('Sincronizacion completada.')

if __name__ == '__main__':
    main()