# AWS Olist Data Pipeline

Pipeline de datos enterprise en AWS — Batch + Real-time + Security

## Stack Técnico
- **S3**: data-pipeline-rob-2026 (arquitectura medallón raw/processed/curated)
- **Glue**: olist_db + ETL olist-etl-transform (PySpark) — schedule 2AM Colombia
- **Athena**: SQL sobre S3 — 99,441 órdenes confirmadas
- **Redshift Serverless**: default-workgroup 8 RPUs — star schema olist
- **QuickSight**: Olist E-Commerce Dashboard
- **Kinesis**: olist-orders-stream (1 shard PROVISIONED)
- **Lambda**: olist-kinesis-processor (Python 3.12, timeout 30s, DLQ)
- **VPC**: olist-vpc (10.0.0.0/16) — 4 subnets 2AZ
- **CloudTrail**: olist-cloudtrail (multi-region)
- **GuardDuty**: activo — detección de amenazas ML
- **Honeypot S3**: olist-secure-backup-rob-2026 → SNS → email
- **Budget Alert**: $5 USD threshold

## Variables de Entorno Lambda
- BUCKET_NAME: bucket destino S3

## Arquitectura
## Costos Estimados
- Kinesis: ~$10.80/mes (1 shard PROVISIONED)
- Redshift: ~$0/mes (serverless, cobra solo al queryar)
- Total stack: ~$12/mes

## ARNs Principales
- Lambda: arn:aws:lambda:us-east-2:611483456967:function:olist-kinesis-processor
- Kinesis: arn:aws:kinesis:us-east-2:611483456967:stream/olist-orders-stream
- VPC: vpc-08fa636cf555aac89
- SNS: arn:aws:sns:us-east-2:611483456967:olist-honeypot-alert
- DLQ: arn:aws:sqs:us-east-2:611483456967:olist-lambda-dlq

## Roadmap
- [ ] Terraform modules
- [ ] S3 Lifecycle rules
- [ ] Step Functions orquestación
- [ ] Pruebas de estrés y latencia
