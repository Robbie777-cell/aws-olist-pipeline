resource "aws_sns_topic" "honeypot_alert" {
  name = "olist-honeypot-alert"

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}