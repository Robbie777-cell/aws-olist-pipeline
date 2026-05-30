variable "aws_region" {
  description = "Región AWS donde se despliega el pipeline"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Nombre del proyecto - cambia esto por cliente"
  type        = string
  default     = "olist"
}

variable "environment" {
  description = "Ambiente del pipeline"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Dueño del pipeline"
  type        = string
  default     = "data-analyst-rob"
} 
