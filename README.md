# Sunrise_Lamp

MicroPython code for Pi Pico to run LED lights with day/night cycle

# Pi Pico Setup

Use Thonny to upload files. There are no good VSCode extensions at this time that can reliably connect and manage files.

## Pi Issues

When the Pi Pico gets stuck in a bootloop or otherwise refuses to connect, use the [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory) option to clear the memory.

# VSCode Setup

The VSCode configuration is not strictly necessary but helps a bit with development experience.

For VSCode typings and error checking to work correctly with MicroPython, setup a venv and the typee stubs using the Pylance options described [here](https://micropython-stubs.readthedocs.io/en/main/index.html).

The requirements-dev.txt is a recommended house keeping file from that process. The .vscode folder contains the VSCode workspace setting overrides.

# Configuration

Copy the config.template.py into a config.py file in the root directory and update with preferred settings.

## Logging to CloudWatch Logs

For logging to AWS, there needs to be an AWS Lambda function configured with a URL endpoint and a secret token environment variable configured that matches the value in the config.py file.

The lambda function requires environment variablese configured like:

-   LOG_GROUP_NAME = /aws/lambda/SUNRISE_LAMP
-   LOG_STREAM_NAME = Pi_Pico_Logs
-   SECRET_TOKEN = Value matching AWS_SECRET_TOKEN from the config.py file
