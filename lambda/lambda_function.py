import json
import base64
import boto3
import datetime
import os

s3  = boto3.client('s3')
sns = boto3.client('sns')

BUCKET    = os.environ['BUCKET_NAME']
SNS_TOPIC = os.environ.get('SNS_TOPIC_ARN', '')

UMBRALES = {
    "nivel_agua_cm": {"critico": 25.0,   "alerta": 40.0},
    "ph":            {"critico": (6.0, 9.0), "alerta": (6.5, 8.5)},
    "oxigeno_mg_l":  {"critico": 2.0,    "alerta": 4.0},
    "turbidez_ntu":  {"critico": 80.0,   "alerta": 60.0},
    "salinidad_ppt": {"critico": 5.0,    "alerta": 4.0},
}


def evaluar_sensor(lectura: dict) -> dict:
    """Evalúa los parámetros del sensor y determina alertas."""
    alertas = []

    # Nivel de agua bajo
    nivel = lectura.get("nivel_agua_cm", 999)
    if nivel < UMBRALES["nivel_agua_cm"]["critico"]:
        alertas.append(f"CRITICO: Nivel de agua {nivel}cm (umbral: {UMBRALES['nivel_agua_cm']['critico']}cm)")
    elif nivel < UMBRALES["nivel_agua_cm"]["alerta"]:
        alertas.append(f"ALERTA: Nivel de agua {nivel}cm (umbral: {UMBRALES['nivel_agua_cm']['alerta']}cm)")

    # pH fuera de rango
    ph = lectura.get("ph", 7.0)
    if ph < UMBRALES["ph"]["critico"][0] or ph > UMBRALES["ph"]["critico"][1]:
        alertas.append(f"CRITICO: pH {ph} fuera de rango crítico {UMBRALES['ph']['critico']}")
    elif ph < UMBRALES["ph"]["alerta"][0] or ph > UMBRALES["ph"]["alerta"][1]:
        alertas.append(f"ALERTA: pH {ph} fuera de rango normal {UMBRALES['ph']['alerta']}")

    # Oxígeno bajo
    oxigeno = lectura.get("oxigeno_mg_l", 999)
    if oxigeno < UMBRALES["oxigeno_mg_l"]["critico"]:
        alertas.append(f"CRITICO: Oxígeno {oxigeno} mg/L (umbral: {UMBRALES['oxigeno_mg_l']['critico']})")
    elif oxigeno < UMBRALES["oxigeno_mg_l"]["alerta"]:
        alertas.append(f"ALERTA: Oxígeno {oxigeno} mg/L (umbral: {UMBRALES['oxigeno_mg_l']['alerta']})")

    # Turbidez alta
    turbidez = lectura.get("turbidez_ntu", 0)
    if turbidez > UMBRALES["turbidez_ntu"]["critico"]:
        alertas.append(f"CRITICO: Turbidez {turbidez} NTU (umbral: {UMBRALES['turbidez_ntu']['critico']})")
    elif turbidez > UMBRALES["turbidez_ntu"]["alerta"]:
        alertas.append(f"ALERTA: Turbidez {turbidez} NTU (umbral: {UMBRALES['turbidez_ntu']['alerta']})")

    return {
        "tiene_alertas": len(alertas) > 0,
        "es_emergencia": lectura.get("estado") in ["EMERGENCIA", "CRITICO"],
        "alertas": alertas
    }


def enviar_alerta_sns(lectura: dict, evaluacion: dict):
    """Envía alerta por SNS cuando se detecta anomalía crítica."""
    if not SNS_TOPIC:
        print("SNS_TOPIC_ARN no configurado — saltando alerta")
        return

    humedal  = lectura.get("humedal", "Desconocido")
    ciudad   = lectura.get("ciudad", "")
    estado   = lectura.get("estado", "DESCONOCIDO")
    salud    = lectura.get("indice_salud", 0)
    sensor   = lectura.get("sensor_id", "")
    ts       = lectura.get("timestamp", "")

    asunto = f"🚨 TINGUA ALERTA [{estado}] — Humedal {humedal}, {ciudad}"

    cuerpo = f"""
╔══════════════════════════════════════════════════════════╗
   SISTEMA TINGUA — Alerta de Humedal
   Tecnología Inteligente para la Gestión y Uso del Agua
╚══════════════════════════════════════════════════════════╝

HUMEDAL:     {humedal} ({ciudad})
SENSOR:      {sensor}
ESTADO:      {estado}
SALUD:       {salud}/100
TIMESTAMP:   {ts}

PARÁMETROS ACTUALES:
  Nivel de agua : {lectura.get('nivel_agua_cm', 'N/A')} cm
  pH            : {lectura.get('ph', 'N/A')}
  Salinidad     : {lectura.get('salinidad_ppt', 'N/A')} ppt
  Temperatura   : {lectura.get('temperatura_c', 'N/A')} °C
  Turbidez      : {lectura.get('turbidez_ntu', 'N/A')} NTU
  Oxígeno       : {lectura.get('oxigeno_mg_l', 'N/A')} mg/L

ALERTAS DETECTADAS:
{chr(10).join(f'  • {a}' for a in evaluacion['alertas'])}

POSIBLES CAUSAS:
  • Extracción ilegal de agua subterránea
  • Sequía crítica por ola de calor
  • Contaminación por actividad agrícola
  • Desvío no autorizado de afluentes

ACCIÓN RECOMENDADA:
  Verificar el humedal {humedal} inmediatamente.
  Coordinar con autoridades hídricas locales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sistema TINGUA | AWS us-east-2 | Proyecto Rob Acosta 2026
    """

    sns.publish(
        TopicArn=SNS_TOPIC,
        Subject=asunto,
        Message=cuerpo.strip()
    )
    print(f"📧 Alerta SNS enviada — {humedal} [{estado}]")


def lambda_handler(event, context):
    procesados  = 0
    alertas_env = 0

    for record in event['Records']:
        # Decodificar payload de Kinesis
        payload  = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        lectura  = json.loads(payload)

        # Determinar si es dato de sensor TINGUA o dato legacy
        es_tingua = lectura.get("proyecto") == "tingua"

        # Guardar en S3
        timestamp = datetime.datetime.utcnow().strftime('%Y/%m/%d/%H')
        prefijo   = "tingua/sensores" if es_tingua else "raw/kinesis"
        humedal   = lectura.get("humedal", "unknown").lower().replace(" ", "-")
        key       = f"{prefijo}/{timestamp}/{humedal}-{record['kinesis']['sequenceNumber']}.json"

        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=payload,
            ContentType='application/json'
        )
        print(f"💾 Guardado: {key}")

        # Evaluar y alertar solo si es dato TINGUA
        if es_tingua:
            evaluacion = evaluar_sensor(lectura)

            estado = lectura.get("estado", "")
            salud  = lectura.get("indice_salud", 100)

            print(
                f"🌿 [{lectura.get('humedal')}] "
                f"Estado: {estado} | "
                f"Salud: {salud}/100 | "
                f"Nivel: {lectura.get('nivel_agua_cm')}cm | "
                f"Alertas: {len(evaluacion['alertas'])}"
            )

            # Disparar SNS si hay emergencia o estado crítico
            if evaluacion["es_emergencia"] and evaluacion["tiene_alertas"]:
                enviar_alerta_sns(lectura, evaluacion)
                alertas_env += 1

        procesados += 1

    return {
        'statusCode': 200,
        'body': json.dumps({
            'procesados': procesados,
            'alertas_enviadas': alertas_env,
            'mensaje': f"TINGUA procesó {procesados} registros, {alertas_env} alertas enviadas"
        })
    }
