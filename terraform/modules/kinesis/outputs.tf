output "stream_name" {
  description = "Nombre del stream Kinesis"
  value       = aws_kinesis_stream.orders.name
}

output "stream_arn" {
  description = "ARN del stream Kinesis"
  value       = aws_kinesis_stream.orders.arn
}