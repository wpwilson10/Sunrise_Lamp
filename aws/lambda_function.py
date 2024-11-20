import os
import json

# TODO - Send logs to CloudWatch Logs.
# TODO - Make more robust to missing messages, etc


def lambda_handler(event, context):
    # Retrieve the token from the environment variable
    expected_token = os.environ.get("SECRET_TOKEN")

    # Check the custom header for the pre-shared token
    headers = event.get("headers", {})
    token = headers.get("X-Custom-Auth")

    # Validate the token
    if token != expected_token:
        return {"statusCode": 403, "body": "Unauthorized"}

    # Process the log message
    log_message = json.loads(event["body"]).get("message", "No message provided")
    print(f"Received log: {log_message}")

    # Example response
    return {"statusCode": 200, "body": "Log received successfully"}
