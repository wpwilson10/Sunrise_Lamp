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
  description = "Named used for AWS CloudWatch Trigger Log Trigger to call Lambda function for error handling"
  type        = string
  default     = "Error_Log_Trigger"
}

variable "secret_token" {
  description = "Shared secret token used to authenticate calls form microcontroller to AWS"
  type        = string
}
