terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
  owner        = var.owner
}

module "kinesis" {
  source       = "./modules/kinesis"
  project_name = var.project_name
  environment  = var.environment
  owner        = var.owner
}

module "lambda" {
  source             = "./modules/lambda"
  project_name       = var.project_name
  environment        = var.environment
  owner              = var.owner
  bucket_name        = module.s3.bucket_id
  kinesis_stream_arn = module.kinesis.stream_arn
}