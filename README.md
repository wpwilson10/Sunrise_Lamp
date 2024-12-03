# Sunrise_Lamp

MicroPython and AWS Lambda function code for a Pi Pico W to run LED lights with day/night cycle.

## Description

The MicroPython code runs on the Pi Pico W to control the LED lights, access scheduling information for controlling the day/night cycle, and logging information back to AWS.

The AWS code uses Lambda functions to receive the log message from the microcontroller and send notifications when an error occurs. Error notifications are based on [this AWS guide](https://aws.amazon.com/blogs/mt/get-notified-specific-lambda-function-error-patterns-using-cloudwatch/).

## Setup

### Configuration Files

Copy the microcontroller/config.template.py into a config.py file in the microcontoller directory and update with preferred settings.

### Pi Pico

Use Thonny to upload the main.py and config.py files to the microcontroller. Setup guide [here](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2). There are no good VSCode extensions at this time that can reliably connect and manage files.

### Logging to CloudWatch Logs

For logging to AWS, there needs to be an AWS Lambda function configured with a URL endpoint and a secret token environment variable configured that matches the value in the config.py file.

The lambda functions require environment variables configured like:

-   logger_lambda
    -   LOG_GROUP_NAME = /aws/lambda/SUNRISE_LAMP
    -   LOG_STREAM_NAME = Pi_Pico_Logs
    -   SECRET_TOKEN = Value matching AWS_SECRET_TOKEN from the config.py file
-   error_log_filter_lambda function
    -   SNS_TOPIC_ARN = ARN of SNS topic that sends notification emails.

### VSCode

The VSCode configuration is not strictly necessary but helps a bit with development experience.

For VSCode typings and error checking to work correctly with MicroPython, setup a venv and the typee stubs using the Pylance options described [here](https://micropython-stubs.readthedocs.io/en/main/index.html).

The requirements-dev.txt is a recommended house keeping file from that process. The .vscode folder contains the VSCode workspace setting overrides.

## Issues

When the Pi Pico gets stuck in a bootloop or otherwise refuses to connect, use the [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory) option to clear the memory.
