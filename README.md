<div align="center">

# 🌊 TINGUA
### Monitor de Humedales Colombianos · Colombian Wetland Monitor

[![Live Dashboard](https://img.shields.io/badge/🌐_Dashboard-Live-0d7fa5?style=for-the-badge)](https://robbie777-cell.github.io/aws-olist-pipeline)
[![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com)
[![Google Earth Engine](https://img.shields.io/badge/Google_Earth_Engine-Sentinel--2-4285F4?style=for-the-badge&logo=google)](https://earthengine.google.com)
[![Cost](https://img.shields.io/badge/Costo_mensual-~$0.00-1a9e6e?style=for-the-badge)](/)

**[🚀 Ver Dashboard en Vivo · Live Dashboard](https://robbie777-cell.github.io/aws-olist-pipeline)**

*Monitoreo satelital en tiempo real de humedales del Caribe colombiano*  
*Real-time satellite monitoring of Colombian Caribbean wetlands*

</div>

---

## 🇨🇴 Español

### ¿Qué es TINGUA?

TINGUA es un sistema de monitoreo ambiental que usa **imágenes satelitales reales de Sentinel-2 (ESA/Copernicus)** procesadas con Google Earth Engine para monitorear el estado de humedales costeros en el Caribe colombiano — con un pipeline serverless en AWS de costo prácticamente cero.

### Humedales monitoreados

| Humedal | NDWI | NDVI | Estado | Imágenes |
|---------|------|------|--------|----------|
| Ciénaga Grande de Santa Marta | -0.015 | 0.169 | ✅ Normal | 80 |
| Ciénaga de Mallorquín | -0.246 | 0.244 | ✅ Normal | 1 |
| Ciénaga de Totumo | -0.133 | 0.140 | ✅ Normal | 1 |

> **NDWI** (Normalized Difference Water Index): mide contenido de agua superficial  
> **NDVI** (Normalized Difference Vegetation Index): mide densidad de vegetación

### Arquitectura del sistema

```
Google Earth Engine (Sentinel-2)
         ↓
   Script Python (GEE API)
         ↓
    Google Drive API
         ↓
   AWS Kinesis (On-Demand)
         ↓
   AWS Lambda (Procesamiento)
         ↓
      AWS S3 (Almacenamiento)
         ↓
   AWS Athena (Consultas SQL)
         ↓
  Dashboard Web (GitHub Pages)
```

### Stack tecnológico

- **Satélite**: Sentinel-2 SR Harmonized — ESA/Copernicus
- **Procesamiento GEE**: `scripts/tingua_gee_to_s3.py`
- **Streaming**: Amazon Kinesis Data Streams (On-Demand)
- **Compute**: AWS Lambda (Python 3.12)
- **Storage**: Amazon S3 (`tingua/gee/` — 4 CSVs, 80 imágenes)
- **Queries**: AWS Athena — `tingua_db.sensor_readings`, `gee_ndwi`, `vista_humedales_completa`
- **Frontend**: HTML + Leaflet.js + Chart.js — GitHub Pages
- **Costo real**: ~$0.00/mes

### Datos en Athena

```sql
-- Vista consolidada (817 registros)
SELECT * FROM tingua_db.vista_humedales_completa LIMIT 10;

-- Serie temporal NDWI
SELECT fecha, ndwi_mean, ndvi_mean
FROM tingua_db.gee_ndwi
ORDER BY fecha;
```

### Estructura del repositorio

```
aws-olist-pipeline/
├── docs/
│   └── index.html          # Dashboard web (GitHub Pages)
├── scripts/
│   └── tingua_gee_to_s3.py # Automatización GEE → S3
├── lambda/
│   └── lambda_function.py  # Procesador Kinesis → S3
├── terraform/              # Infraestructura como código
└── README.md
```

### Cómo correr el pipeline

```bash
# 1. Instalar dependencias
pip install earthengine-api google-auth pandas boto3

# 2. Autenticar Google Earth Engine
earthengine authenticate

# 3. Correr extracción de datos satelitales
python scripts/tingua_gee_to_s3.py

# 4. Consultar datos en Athena
# Base de datos: tingua_db
# Tabla principal: vista_humedales_completa
```

### Roadmap

- [x] Pipeline AWS serverless (Kinesis + Lambda + S3 + Athena)
- [x] Integración Google Earth Engine con Sentinel-2
- [x] Serie temporal 80 imágenes Ene–Jun 2026
- [x] Dashboard web mobile-responsive
- [ ] Expandir a 10+ humedales del Caribe colombiano
- [ ] Alertas automáticas por email/WhatsApp
- [ ] API REST para consumo externo (IDEAM, CRAs)

---

## 🇺🇸 English

### What is TINGUA?

TINGUA is an environmental monitoring system that uses **real Sentinel-2 satellite imagery (ESA/Copernicus)** processed with Google Earth Engine to track the health of coastal wetlands in the Colombian Caribbean — running on a near-zero-cost AWS serverless pipeline.

### Monitored Wetlands

| Wetland | NDWI | NDVI | Status | Images |
|---------|------|------|--------|--------|
| Ciénaga Grande de Santa Marta | -0.015 | 0.169 | ✅ Normal | 80 |
| Ciénaga de Mallorquín | -0.246 | 0.244 | ✅ Normal | 1 |
| Ciénaga de Totumo | -0.133 | 0.140 | ✅ Normal | 1 |

### System Architecture

```
Google Earth Engine (Sentinel-2 satellite imagery)
         ↓
   Python Script (GEE API extraction)
         ↓
    Google Drive API (intermediate transfer)
         ↓
   AWS Kinesis Data Streams (On-Demand ingestion)
         ↓
   AWS Lambda (serverless processing)
         ↓
      AWS S3 (data lake storage)
         ↓
   AWS Athena (SQL analytics)
         ↓
  Web Dashboard (GitHub Pages — live)
```

### Tech Stack

- **Satellite data**: Sentinel-2 SR Harmonized — ESA/Copernicus (real imagery)
- **GEE processing**: `scripts/tingua_gee_to_s3.py`
- **Streaming**: Amazon Kinesis Data Streams (On-Demand)
- **Compute**: AWS Lambda (Python 3.12)
- **Storage**: Amazon S3 (`tingua/gee/` — 4 CSVs, 80 satellite images)
- **Analytics**: AWS Athena — 817 records in `vista_humedales_completa`
- **Frontend**: HTML + Leaflet.js + Chart.js — GitHub Pages
- **Monthly cost**: ~$0.00

### Roadmap

- [x] Serverless AWS pipeline (Kinesis + Lambda + S3 + Athena)
- [x] Google Earth Engine integration with real Sentinel-2 data
- [x] 80-image temporal series Jan–Jun 2026
- [x] Mobile-responsive web dashboard
- [ ] Expand to 10+ Caribbean Colombia wetlands
- [ ] Automated alerts via email/WhatsApp
- [ ] REST API for external consumption (IDEAM, CRAs)

---

<div align="center">

**Built with real satellite data · Construido con datos satelitales reales**

[🌐 Live Dashboard](https://robbie777-cell.github.io/aws-olist-pipeline) · [AWS Account: 611483456967] · [Region: us-east-2]

*Rob Acosta · Data Engineer · Barranquilla, Colombia · 2026*

</div>
