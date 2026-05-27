import json, base64, boto3, datetime, os

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        order = json.loads(payload)
        timestamp = datetime.datetime.utcnow().strftime('%Y/%m/%d/%H')
        key = f"raw/kinesis/{timestamp}/{record['kinesis']['sequenceNumber']}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=payload, ContentType='application/json')
        print(f"Guardado: {key}")
    return {'statusCode': 200, 'body': f"Procesados {len(event['Records'])} registros"}
