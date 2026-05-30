resource "aws_s3_bucket" "data_pipeline" {
  bucket = "data-pipeline-rob-2026"

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "data_pipeline" {
  bucket = aws_s3_bucket.data_pipeline.id

  versioning_configuration {
    status = "Enabled"
  }
}