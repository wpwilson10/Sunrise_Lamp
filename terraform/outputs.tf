output "lambda_function_url" {
  description = "URL to use as AWS_LOG_URL in the microcontroller's config.py"
  value       = module.logger_lambda.lambda_function_url
}
