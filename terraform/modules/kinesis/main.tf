resource "aws_kinesis_stream" "orders" {
  name        = "olist-orders-stream"
  shard_count = 1

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}