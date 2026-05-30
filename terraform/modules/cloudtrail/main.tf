resource "aws_cloudtrail" "olist" {
  name                          = "olist-cloudtrail"
  s3_bucket_name                = var.cloudtrail_bucket
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  include_global_service_events = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::olist-secure-backup-rob-2026/"]
    }
  }

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}