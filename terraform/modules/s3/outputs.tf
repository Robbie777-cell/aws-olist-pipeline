output "bucket_id" {
  description = "ID del bucket S3"
  value       = aws_s3_bucket.data_pipeline.id
}

output "bucket_arn" {
  description = "ARN del bucket S3"
  value       = aws_s3_bucket.data_pipeline.arn
}