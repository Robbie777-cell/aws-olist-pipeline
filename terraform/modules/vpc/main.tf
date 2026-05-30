resource "aws_vpc" "olist" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
    Name        = "olist-vpc"
  }
}