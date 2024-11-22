import os
import json

import json
import os
import boto3
import time
import logging

# Set up the boto3 client for CloudWatch Logs
cloudwatch_logs_client = boto3.client("logs")

# Define environment variables for the log group and stream
LOG_GROUP_NAME: str = os.environ.get("LOG_GROUP_NAME", "Sunrise_Lamp")
LOG_STREAM_NAME: str = os.environ.get("LOG_STREAM_NAME", "Default_Stream")

# Logger for debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_or_create_log_group_and_stream():
    """Ensures the log group and stream exist in CloudWatch Logs."""
    try:
        # Ensure the log group exists
        cloudwatch_logs_client.create_log_group(logGroupName=LOG_GROUP_NAME)
        logger.info(f"Created log group: {LOG_GROUP_NAME}")
    except cloudwatch_logs_client.exceptions.ResourceAlreadyExistsException:
        logger.info(f"Log group {LOG_GROUP_NAME} already exists.")

    try:
        # Ensure the log stream exists
        cloudwatch_logs_client.create_log_stream(
            logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME
        )
        logger.info(f"Created log stream: {LOG_STREAM_NAME}")
    except cloudwatch_logs_client.exceptions.ResourceAlreadyExistsException:
        logger.info(f"Log stream {LOG_STREAM_NAME} already exists.")


def log_to_cloudwatch(message, level):
    """
    Sends a log entry to CloudWatch Logs.

    Args:
        message (str): The log message.
        level (str): The log level (e.g., INFO, ERROR).
    """
    global sequence_token

    log_event = {
        "timestamp": int(time.time() * 1000),  # Milliseconds since epoch
        "message": f"{level} | {message}",
    }

    try:
        # Construct the put_log_events request
        kwargs = {
            "logGroupName": LOG_GROUP_NAME,
            "logStreamName": LOG_STREAM_NAME,
            "logEvents": [log_event],
        }

        # Send the log event
        response = cloudwatch_logs_client.put_log_events(**kwargs)

    except Exception as e:
        logger.error(f"Failed to send log to CloudWatch: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda function entry point.

    Parses a log message sent from the Pi Pico and writes it to CloudWatch Logs.

    Args:
        event (dict): The input event to the Lambda function (contains the log message).
        context (LambdaContext): The runtime information of the Lambda function.
    """
    # Check the custom header for the pre-shared token
    headers = event.get("headers", {})
    # Lowercase is important for HTTP 2 protocol
    token = headers.get("x-custom-auth")

    # Validate the token
    if token != os.environ.get("SECRET_TOKEN"):
        return {"statusCode": 403, "body": "Unauthorized"}

    get_or_create_log_group_and_stream()

    # Parse the incoming request body
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "No message provided")
        level = body.get("level", "INFO").upper()

        log_to_cloudwatch(message, level)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Log saved to CloudWatch."}),
        }
    except json.JSONDecodeError:
        logger.error("Failed to parse request body.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format."}),
        }
    except Exception as e:
        logger.error(f"Error processing log: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error."}),
        }
