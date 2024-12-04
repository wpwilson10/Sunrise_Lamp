locals {
  lambda_runtime      = "python3.13"
  lambda_architecture = ["arm64"]
  lambda_handler      = "lambda_function.lambda_handler"
  cw_logs_full_arn    = "${aws_cloudwatch_log_group.this.arn}:*" # https://github.com/hashicorp/terraform-provider-aws/issues/22957
}

resource "aws_sns_topic" "this" {
  name = "TF_Topic"
}

resource "aws_sns_topic_subscription" "this" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "email"
  endpoint  = var.sns_destination_email
}

resource "aws_cloudwatch_log_group" "this" {
  name              = var.log_group_name
  retention_in_days = 90
}

resource "aws_cloudwatch_log_stream" "this" {
  name           = var.log_stream_name
  log_group_name = aws_cloudwatch_log_group.this.name
}

resource "aws_cloudwatch_log_subscription_filter" "this" {
  name            = var.log_trigger_name
  log_group_name  = aws_cloudwatch_log_group.this.name
  filter_pattern  = "%ERROR%"
  destination_arn = module.error_log_filter_lambda.lambda_function_arn
}

module "logger_lambda" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "7.16.0"
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture

  function_name              = "tf_logger"
  description                = "Lambda from TF for WPW_SUNRISE_LAMP"
  source_path                = "../aws/logger"
  publish                    = true
  create_lambda_function_url = true

  environment_variables = {
    LOG_GROUP_NAME  = aws_cloudwatch_log_group.this.name
    LOG_STREAM_NAME = aws_cloudwatch_log_stream.this.name
    SECRET_TOKEN    = var.secret_token
  }

  attach_policy_statements = true
  policy_statements = {
    logs_put = {
      effect    = "Allow",
      actions   = ["logs:PutLogEvents"],
      resources = [local.cw_logs_full_arn]
    }
  }
}

module "error_log_filter_lambda" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "7.16.0"
  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture

  function_name = "tf_error_filter"
  description   = "Lambda from TF for ERROR_LOG_FILTER"
  source_path   = "../aws/error_trigger"
  publish       = true

  environment_variables = {
    SNS_TOPIC_ARN = aws_sns_topic.this.arn
  }

  attach_policy_statements = true
  policy_statements = {
    logs_put = {
      effect    = "Allow",
      actions   = ["sns:Publish"],
      resources = [aws_sns_topic.this.arn]
    }
  }

  allowed_triggers = {
    CloudWatchLogs = {
      principal  = "logs.amazonaws.com"
      source_arn = local.cw_logs_full_arn
    }
  }
}
