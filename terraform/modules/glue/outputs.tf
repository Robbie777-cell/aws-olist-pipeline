output "database_name" {
  value = aws_glue_catalog_database.olist.name
}
output "job_name" {
  value = aws_glue_job.etl_transform.name
}