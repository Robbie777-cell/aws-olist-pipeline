resource "aws_kinesis_stream" "orders" {
  name = "${var.project_name}-orders-stream"

  stream_mode_details {
    stream_mode = "ON_DEMAND"
  }

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
