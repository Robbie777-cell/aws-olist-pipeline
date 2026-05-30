output "lambda_arn" {
  value = aws_lambda_function.kinesis_processor.arn
}
output "lambda_name" {
  value = aws_lambda_function.kinesis_processor.function_name
}