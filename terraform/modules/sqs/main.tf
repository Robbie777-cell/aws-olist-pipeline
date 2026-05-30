resource "aws_sqs_queue" "dlq" {
  name                      = "olist-lambda-dlq"
  message_retention_seconds = 1209600

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  lifecycle {
    ignore_changes = [max_message_size]
  }
}