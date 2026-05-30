variable "project_name" {
  type = string
}
variable "environment" {
  type = string
}
variable "owner" {
  type = string
}
variable "bucket_name" {
  type = string
}
variable "kinesis_stream_arn" {
  type = string
}
variable "lambda_zip_path" {
  type    = string
  default = "./lambda.zip"
}