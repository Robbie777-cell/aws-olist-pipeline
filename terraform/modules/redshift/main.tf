resource "aws_redshiftserverless_namespace" "olist" {
  namespace_name = "${var.project_name}-namespace"
  db_name        = "dev"
  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  lifecycle {
    ignore_changes = [
      admin_username,
      admin_user_password,
      manage_admin_password,
      default_iam_role_arn,
      iam_roles,
      kms_key_id,
      log_exports
    ]
  }
}
resource "aws_redshiftserverless_workgroup" "olist" {
  namespace_name = "${var.project_name}-namespace"
  workgroup_name = "${var.project_name}-workgroup"
  base_capacity  = 8
  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  lifecycle {
    ignore_changes = [
      config_parameter,
      price_performance_target,
      security_group_ids,
      subnet_ids,
      enhanced_vpc_routing,
      publicly_accessible,
      max_capacity
    ]
  }
}
