#!/usr/bin/env python3
"""
TINGUA — Simulador de Sensores de Humedal
==========================================
Simula lecturas de sensores IoT en humedales colombianos
y las envía al Kinesis Data Stream en tiempo real.

Uso:
    python sensor_simulator.py
    python sensor_simulator.py --stream tingua-orders-stream --region us-east-2 --interval 5
"""

import json
import time
import random
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

# ─── Configuración de logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("tingua-sensor")

# ─── Humedales colombianos objetivo ──────────────────────────────────────────
HUMEDALES = [
    {"id": "JAB-001", "nombre": "Jaboque",         "ciudad": "Bogota",      "lat": 4.7110,  "lon": -74.1231},
    {"id": "TIN-001", "nombre": "Torca-Guaymaral", "ciudad": "Bogota",      "lat": 4.7864,  "lon": -74.0539},
    {"id": "COR-001", "nombre": "Cordoba",          "ciudad": "Bogota",      "lat": 4.7207,  "lon": -74.0749},
    {"id": "SAN-001", "nombre": "Santa Maria",      "ciudad": "Bogota",      "lat": 4.6397,  "lon": -74.1073},
    {"id": "CIE-001", "nombre": "Cienaga Grande",   "ciudad": "Santa Marta", "lat": 10.8380, "lon": -74.4700},
    {"id": "BAM-001", "nombre": "Bamdej",           "ciudad": "Meta",        "lat": 3.9200,  "lon": -73.1500},
]

# ─── Rangos normales por parámetro ───────────────────────────────────────────
RANGOS = {
    "nivel_agua_cm":  {"min": 20.0,  "max": 120.0, "critico_min": 25.0,  "critico_max": 110.0},
    "ph":             {"min": 6.0,   "max": 9.0,   "critico_min": 6.5,   "critico_max": 8.5},
    "salinidad_ppt":  {"min": 0.1,   "max": 5.0,   "critico_min": 0.2,   "critico_max": 4.0},
    "temperatura_c":  {"min": 15.0,  "max": 32.0,  "critico_min": 16.0,  "critico_max": 30.0},
    "turbidez_ntu":   {"min": 1.0,   "max": 80.0,  "critico_min": 5.0,   "critico_max": 60.0},
    "oxigeno_mg_l":   {"min": 2.0,   "max": 12.0,  "critico_min": 4.0,   "critico_max": 10.0},
}


def generar_lectura(humedal: Dict, anomalia: bool = False) -> Dict[str, Any]:
    """
    Genera una lectura realista de un sensor de humedal.
    Si anomalia=True, genera valores fuera del rango crítico
    para simular una alerta de extracción ilegal o sequía.
    """
    def valor(param: str) -> float:
        r = RANGOS[param]
        if anomalia and param in ["nivel_agua_cm", "oxigeno_mg_l"]:
            # Simular nivel crítico bajo (posible extracción ilegal)
            return round(random.uniform(r["min"], r["critico_min"]), 2)
        if anomalia and param in ["salinidad_ppt", "turbidez_ntu"]:
            # Simular contaminación
            return round(random.uniform(r["critico_max"], r["max"]), 2)
        # Lectura normal con pequeña variación
        base = (r["critico_min"] + r["critico_max"]) / 2
        variacion = (r["critico_max"] - r["critico_min"]) * 0.3
        return round(random.uniform(base - variacion, base + variacion), 2)

    lectura = {
        "sensor_id":       f"tingua-sensor-{humedal['id']}",
        "humedal":         humedal["nombre"],
        "ciudad":          humedal["ciudad"],
        "latitud":         humedal["lat"],
        "longitud":        humedal["lon"],
        "nivel_agua_cm":   valor("nivel_agua_cm"),
        "ph":              valor("ph"),
        "salinidad_ppt":   valor("salinidad_ppt"),
        "temperatura_c":   valor("temperatura_c"),
        "turbidez_ntu":    valor("turbidez_ntu"),
        "oxigeno_mg_l":    valor("oxigeno_mg_l"),
        "anomalia":        anomalia,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "version":         "1.0",
        "proyecto":        "tingua",
    }

    # Calcular índice de salud del humedal (0-100)
    salud = calcular_salud(lectura)
    lectura["indice_salud"] = salud
    lectura["estado"] = clasificar_estado(salud)

    return lectura


def calcular_salud(lectura: Dict) -> int:
    """
    Calcula un índice de salud del humedal (0-100)
    basado en los parámetros medidos.
    """
    puntos = 100

    # Penalizar nivel bajo de agua
    if lectura["nivel_agua_cm"] < RANGOS["nivel_agua_cm"]["critico_min"]:
        puntos -= 30
    # Penalizar pH fuera de rango
    if not (RANGOS["ph"]["critico_min"] <= lectura["ph"] <= RANGOS["ph"]["critico_max"]):
        puntos -= 20
    # Penalizar oxígeno bajo
    if lectura["oxigeno_mg_l"] < RANGOS["oxigeno_mg_l"]["critico_min"]:
        puntos -= 25
    # Penalizar turbidez alta
    if lectura["turbidez_ntu"] > RANGOS["turbidez_ntu"]["critico_max"]:
        puntos -= 15
    # Penalizar salinidad alta
    if lectura["salinidad_ppt"] > RANGOS["salinidad_ppt"]["critico_max"]:
        puntos -= 10

    return max(0, puntos)


def clasificar_estado(salud: int) -> str:
    if salud >= 80:
        return "SALUDABLE"
    elif salud >= 60:
        return "ALERTA"
    elif salud >= 40:
        return "CRITICO"
    else:
        return "EMERGENCIA"


def enviar_a_kinesis(
    cliente_kinesis,
    stream_name: str,
    lectura: Dict
) -> bool:
    """Envía una lectura al Kinesis Data Stream."""
    try:
        response = cliente_kinesis.put_record(
            StreamName=stream_name,
            Data=json.dumps(lectura, ensure_ascii=False),
            PartitionKey=lectura["sensor_id"]
        )
        shard_id = response.get("ShardId", "?")
        seq = response.get("SequenceNumber", "?")[:8]
        log.info(
            f"✓ [{lectura['humedal']}] Estado: {lectura['estado']} "
            f"| Nivel: {lectura['nivel_agua_cm']}cm "
            f"| pH: {lectura['ph']} "
            f"| Salud: {lectura['indice_salud']}/100 "
            f"→ Shard: {shard_id} Seq: {seq}..."
        )
        return True

    except ClientError as e:
        log.error(f"✗ Error enviando a Kinesis: {e.response['Error']['Message']}")
        return False


def simular(stream_name: str, region: str, intervalo: int, max_registros: int = 0):
    """
    Loop principal del simulador.
    Envía lecturas de todos los humedales al stream de Kinesis.
    """
    log.info("=" * 60)
    log.info("🌿 TINGUA — Simulador de Sensores de Humedal")
    log.info(f"   Stream:   {stream_name}")
    log.info(f"   Región:   {region}")
    log.info(f"   Intervalo: {intervalo}s")
    log.info(f"   Humedales: {len(HUMEDALES)}")
    log.info("=" * 60)

    cliente = boto3.client("kinesis", region_name=region)
    contador = 0

    try:
        while True:
            for humedal in HUMEDALES:
                # 10% de probabilidad de generar una anomalía
                anomalia = random.random() < 0.10

                lectura = generar_lectura(humedal, anomalia=anomalia)

                if anomalia:
                    log.warning(
                        f"⚠ ANOMALÍA detectada en {humedal['nombre']} "
                        f"— Posible extracción ilegal o sequía crítica"
                    )

                enviado = enviar_a_kinesis(cliente, stream_name, lectura)

                if enviado:
                    contador += 1

                if max_registros > 0 and contador >= max_registros:
                    log.info(f"✅ Completados {contador} registros. Fin del simulador.")
                    return

            log.info(f"--- Ciclo completo | Total enviado: {contador} registros ---")
            time.sleep(intervalo)

    except KeyboardInterrupt:
        log.info(f"\n🛑 Simulador detenido por el usuario. Total enviado: {contador} registros.")


def main():
    parser = argparse.ArgumentParser(
        description="TINGUA — Simulador de sensores de humedales colombianos"
    )
    parser.add_argument(
        "--stream",
        default="olist-orders-stream",
        help="Nombre del Kinesis Data Stream (default: olist-orders-stream)"
    )
    parser.add_argument(
        "--region",
        default="us-east-2",
        help="Región AWS (default: us-east-2)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Segundos entre cada ciclo de envío (default: 5)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=0,
        help="Máximo de registros a enviar (0 = infinito)"
    )

    args = parser.parse_args()
    simular(
        stream_name=args.stream,
        region=args.region,
        intervalo=args.interval,
        max_registros=args.max
    )


if __name__ == "__main__":
    main()
