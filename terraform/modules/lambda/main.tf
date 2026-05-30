resource "aws_lambda_function" "kinesis_processor" {
  function_name = "olist-kinesis-processor"
  role          = "arn:aws:iam::611483456967:role/service-role/olist-kinesis-processor-role-9htvhlrr"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30
  filename      = "lambda.zip"

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
    }
  }

  dead_letter_config {
    target_arn = "arn:aws:sqs:us-east-2:611483456967:olist-lambda-dlq"
  }

  vpc_config {
    subnet_ids         = ["subnet-08cc798197b911eb9", "subnet-0e4019d445f99c899"]
    security_group_ids = ["sg-0672f546131b86b4e"]
  }

  tags = {
    Project     = "${var.project_name}-pipeline"
    Owner       = var.owner
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }
}

resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = var.kinesis_stream_arn
  function_name     = aws_lambda_function.kinesis_processor.arn
  starting_position = "LATEST"
  batch_size        = 100
}