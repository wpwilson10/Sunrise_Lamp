# Sunrise_Lamp

MicroPython code for implementing an LED lighting control system using a Pi Pico W to simulate natural lighting cycles.

## Description

This project implements a smart lighting control system designed to simulate natural lighting cycles. The system controls two LED channels (warm and cool), transitions smoothly between lighting states, and integrates with cloud services for logging. It uses a microcontroller (e.g., Raspberry Pi Pico W) running MicroPython.

### Features

Smooth brightness transitions for warm and cool LEDs simulating sunrise and sunset.

Automatically calculates sunset and timezone offsets using internet APIs given the configured coordinate location.

Multiple lighting modes:

-   night light: consistent dim warm lighting
-   sunrise: warm lights increase in brightness
-   daylight: cool lights power on and increase to full brightness
-   sunset: cool lights dim until just warm lights are powered
-   bedtime: warm lights dim

Scheduled tasks to update lighting modes dynamically.

Logs events and errors to AWS via a URL endpoint.

## Setup

### Configuration

Copy the microcontroller/config.template.py into a config.py file and update with preferred settings.

Required variables:

-   AWS_LOG_URL - the API endpoint that logs messages from the microcontroller
-   AWS_SECRET_TOKEN - this should match secret_token above
-   WIFI_SSID
-   WIFI_PASSWORD

### Pi Pico Installation

Use Thonny to upload the main.py and config.py files to the microcontroller. Setup guide [here](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2). There are no good VSCode extensions at this time that can reliably connect and manage files.

### VSCode

The VSCode configuration is not strictly necessary but helps a bit with development experience.

For VSCode typings and error checking to work correctly with MicroPython, setup a venv and the typee stubs using the Pylance options described [here](https://micropython-stubs.readthedocs.io/en/main/index.html).

The requirements-dev.txt is a recommended house keeping file from that process. The .vscode folder contains the VSCode workspace setting overrides.

## Issues

When the Pi Pico gets stuck in a bootloop or otherwise refuses to connect, use the [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory) option to clear the memory.
