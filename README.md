# Sunrise_Lamp

MicroPython, AWS Lambda function code, and Terraform configuration for a Pi Pico W to run LED lights with a configurable day/night cycle via integration with AWS services.

## Description

The MicroPython code runs on the Pi Pico W to control the LED lights, access scheduling information for controlling the day/night cycle, and logging information back to AWS.

The AWS code uses Lambda functions to receive the log message from the microcontroller and send notifications when an error occurs. The architecture is based on [this AWS guide](https://aws.amazon.com/blogs/mt/get-notified-specific-lambda-function-error-patterns-using-cloudwatch/).

Briefly, the microcontoller acts as a client and sends logs via an HTTPS Post request to a Lambda URL endpoint. This first Lambda function verifies the source and saves the log to CloudWatch logs. Then a CloudWatch Log subscription filter checks for logs containing "ERROR" and sends them to a second Lambda function. This second Lambda function forwards the log to SNS where it gets sent via email to a recepient.

![alt text](https://d2908q01vomqb2.cloudfront.net/972a67c48192728a34979d9a35164c1295401b71/2020/08/10/customlambdaerror_arch.png)

Included Terraform configurations is used to fully automate the AWS build.

## Setup

### Configuration

An AWS account must exist and credentials configured as described [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

1. Create a terraform.tfvars file in ./terraform to configure the AWS build. See variables.tf for more information. Review the locals variables in main.terraform if performing significant code changes.
    - Required variables:
        - sns_destination_email - this email will need to be verified using an automatic verification email before it can receive notifications.
        - secret_token - this should match AWS_SECRET_TOKEN below
2. Copy the microcontroller/config.template.py into a config.py file and update with preferred settings.
    - Required variables:
        - AWS_LOG_URL - this should match the given output URL from the Terraform AWS build
        - AWS_SECRET_TOKEN - this should match secret_token above
        - WIFI_SSID
        - WIFI_PASSWORD

### AWS using Terraform

Once the configuration above is complete, run the following commands from the ./terraform directory.

```
terraform init
terraform plan
terraform apply
```

### Pi Pico

Use Thonny to upload the main.py and config.py files to the microcontroller. Setup guide [here](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2). There are no good VSCode extensions at this time that can reliably connect and manage files.

### VSCode

The VSCode configuration is not strictly necessary but helps a bit with development experience.

For VSCode typings and error checking to work correctly with MicroPython, setup a venv and the typee stubs using the Pylance options described [here](https://micropython-stubs.readthedocs.io/en/main/index.html).

The requirements-dev.txt is a recommended house keeping file from that process. The .vscode folder contains the VSCode workspace setting overrides.

## Issues

When the Pi Pico gets stuck in a bootloop or otherwise refuses to connect, use the [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory) option to clear the memory.
