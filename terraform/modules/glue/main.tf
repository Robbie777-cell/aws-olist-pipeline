resource "aws_glue_catalog_database" "olist" {
  name = "olist_db"
}

resource "aws_glue_job" "etl_transform" {
  name     = "olist-etl-transform"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.glue_assets_bucket}/scripts/olist-etl-transform.py"
    python_version  = "3"
  }

  glue_version      = "5.1"
  number_of_workers = 2
  worker_type       = "G.1X"

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  lifecycle {
    ignore_changes = [command]
  }
}