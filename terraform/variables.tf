# Uses the access credential values in the profile located at
#  "~/.aws/credentials" (Linux) or "%USERPROFILE%\.aws\credentials" (Windows).
# See https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
variable "credentials_profile" {
  description = "Profile to use from the AWS credentials file"
  type        = string
  default     = "default"
}

variable "region" {
  description = "AWS Region to use for this account"
  type        = string
  default     = "us-east-1"
}

variable "sns_topic_name" {
  description = "Name of SNS Topic that sends error notification emails"
  type        = string
  default     = "Default_Topic"
}

variable "sns_destination_email" {
  description = "Email address used as SNS subscription endpoint to send error notifications"
  type        = string
}

variable "log_group_name" {
  description = "Named used for AWS CloudWatch Logs Group"
  type        = string
  default     = "Default_Logger"
}

variable "log_stream_name" {
  description = "Named used for AWS CloudWatch Logs Group Stream"
  type        = string
  default     = "Default_Stream"
}

variable "log_trigger_name" {
  description = "Named used for AWS CloudWatch Log Trigger to call Lambda function for error handling"
  type        = string
  default     = "Error_Log_Trigger"
}

variable "lambda_logger_name" {
  description = "Named used for AWS Lambda function that accepts log messages from the microcontoller"
  type        = string
  default     = "Logger_Function"
}

variable "lambda_error_name" {
  description = "Named used for AWS Lambda function that sends error log messages to SNS"
  type        = string
  default     = "Error_Function"
}

variable "secret_token" {
  description = "Shared secret token used to authenticate calls form microcontroller to AWS"
  type        = string
  default     = "my_secure_static_token_12345"
}
