output "aws_region" {
  description = "Región donde está desplegado el pipeline"
  value       = var.aws_region
}

output "project_name" {
  description = "Nombre del proyecto"
  value       = var.project_name
}

output "environment" {
  description = "Ambiente del pipeline"
  value       = var.environment
} 
