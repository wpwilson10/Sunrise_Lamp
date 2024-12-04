provider "aws" {
  region  = var.region
  profile = var.credentials_profile

  default_tags {
    tags = {
      Terraform = "True"
    }
  }
}

locals {
  lambda_runtime      = "python3.13"
  lambda_architecture = ["arm64"]
  lambda_handler      = "lambda_function.lambda_handler"
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

module "logger_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.16.0"

  function_name              = "tf_logger"
  description                = "Lambda from TF for WPW_SUNRISE_LAMP"
  source_path                = "../aws/logger"
  create_lambda_function_url = true

  environment_variables = {
    LOG_GROUP_NAME  = var.log_group_name
    LOG_STREAM_NAME = var.log_stream_name
    SECRET_TOKEN    = var.secret_token
  }

  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture
}

module "error_log_filter_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.16.0"

  function_name = "tf_error_filter"
  description   = "Lambda from TF for ERROR_LOG_FILTER"
  source_path   = "../aws/error_trigger"

  environment_variables = {
    SNS_TOPIC_ARN = aws_sns_topic.this.arn
  }

  handler       = local.lambda_handler
  runtime       = local.lambda_runtime
  architectures = local.lambda_architecture
}
