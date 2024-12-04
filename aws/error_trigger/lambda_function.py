import boto3
import gzip
import json
import os
import logging
from base64 import b64decode

# Read environment variables
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
AWS_REGION = os.environ.get(
    "AWS_REGION", "us-east-1"
)  # Default to us-east-1 if not provided

# Initialize the SNS client
sns_client = boto3.client("sns", region_name=AWS_REGION)

# Logger for debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to process CloudWatch Logs and send error-level logs to an SNS topic.

    Args:
        event (dict): The incoming event containing CloudWatch Logs.
        context: Lambda context object.

    Returns:
        dict: Success or failure message.
    """
    try:
        # Decode and decompress the CloudWatch log data
        compressed_payload = b64decode(event["awslogs"]["data"])
        decompressed_payload = gzip.decompress(compressed_payload)
        log_data = json.loads(decompressed_payload)

        # Iterate through log events
        for log_event in log_data["logEvents"]:
            message = log_event["message"]

            # Example check for error-level logs
            if "ERROR" in message.upper():
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="AWS Error Notification",
                    Message=f"Log Group: {log_data['logGroup']}\n"
                    f"Log Stream: {log_data['logStream']}\n"
                    f"Message: {message}",
                )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Logs processed successfully."}),
        }
    except Exception as e:
        logger.error(f"Error processing logs: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error processing logs.", "error": str(e)}),
        }
