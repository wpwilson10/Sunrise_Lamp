locals {
  lambda_runtime      = "python3.13"
  lambda_architecture = ["arm64"]
  lambda_handler      = "lambda_function.lambda_handler"         # https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
  cw_logs_full_arn    = "${aws_cloudwatch_log_group.this.arn}:*" # https://github.com/hashicorp/terraform-provider-aws/issues/22957
}

# Sends messages from Lambda to specific destinations
resource "aws_sns_topic" "this" {
  name = var.sns_topic_name
}

# Directs messages to a given email
resource "aws_sns_topic_subscription" "this" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "email"
  endpoint  = var.sns_destination_email
}

# Stores log messages from Lambda
resource "aws_cloudwatch_log_group" "this" {
  name              = var.log_group_name
  retention_in_days = 90
}

# Specific logging stream for easier discovery
resource "aws_cloudwatch_log_stream" "this" {
  name           = var.log_stream_name
  log_group_name = aws_cloudwatch_log_group.this.name
}

# Used to send logs containing ERROR to error_log_lambda
resource "aws_cloudwatch_log_subscription_filter" "this" {
  name            = var.log_trigger_name
  log_group_name  = aws_cloudwatch_log_group.this.name
  filter_pattern  = "%ERROR%"
  destination_arn = module.error_log_filter_lambda.lambda_function_arn
}

# Function that receives HTTPS PUTS from microcontoller and stores in CW Logs
module "logger_lambda" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "7.16.0"
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture

  function_name                     = var.lambda_logger_name
  description                       = "Puts messages from microcontroller client into CW Logs"
  source_path                       = "../aws/logger" # Directory containing Lambda function code
  publish                           = true
  create_lambda_function_url        = true # Gives us a public endpoint for sending messages
  cloudwatch_logs_retention_in_days = 90

  # matches variables used in function code
  environment_variables = {
    LOG_GROUP_NAME  = aws_cloudwatch_log_group.this.name
    LOG_STREAM_NAME = aws_cloudwatch_log_stream.this.name
    SECRET_TOKEN    = var.secret_token
  }

  # allows saving logs to our specific CW Log group
  attach_policy_statements = true
  policy_statements = {
    logs_put = {
      effect    = "Allow",
      actions   = ["logs:PutLogEvents"],
      resources = [local.cw_logs_full_arn]
    }
  }
}

# Function that takes error messages and sends them to SNS (because CW Logs cannot do this directly)
module "error_log_lambda" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "7.16.0"
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture

  function_name                     = var.lambda_error_name
  description                       = "Fowards error logs from CW Logs to SNS for proactive notification"
  source_path                       = "../aws/error_trigger" # Directory containing Lambda function code
  publish                           = true
  cloudwatch_logs_retention_in_days = 90

  # matches variables used in function code
  environment_variables = {
    SNS_TOPIC_ARN = aws_sns_topic.this.arn
  }

  # allows sending notifications to SNS
  attach_policy_statements = true
  policy_statements = {
    logs_put = {
      effect    = "Allow",
      actions   = ["sns:Publish"],
      resources = [aws_sns_topic.this.arn]
    }
  }

  # allows CW Logs to invoke function
  allowed_triggers = {
    CloudWatchLogs = {
      principal  = "logs.amazonaws.com"
      source_arn = local.cw_logs_full_arn
    }
  }
}
