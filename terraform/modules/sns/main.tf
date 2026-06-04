resource "aws_sns_topic" "honeypot_alert" {
  name = "${var.project_name}-honeypot-alert"
  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
