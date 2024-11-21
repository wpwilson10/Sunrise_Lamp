# Sunrise_Lamp

MicroPython code for Pi Pico to run LED lights with day/night cycle

# Pi Pico Setup

Use Thonny to upload files. There are no good VSCode extensions at this time that can reliably connect and manage files.

This build uses some micropython-lib modules which much be installed using Thonny:

-   [logging](https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging)
-   [time](https://github.com/micropython/micropython-lib/tree/master/python-stdlib/time)

## Pi Issues

When the Pi Pico gets stuck in a bootloop or otherwise refuses to connect, use the [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory) option to clear the memory.

# VSCode Setup

The VSCode configuration is not strictly necessary but helps a bit with development experience.

For VSCode typings and error checking to work correctly with MicroPython, setup a venv and the typee stubs using the following with the Pylance options:

-   https://micropython-stubs.readthedocs.io/en/main/index.html

The requirements-dev.txt is a recommended house keeping file from that process. The .vscode folder contains the VSCode workspace setting overrides.

# Configuration

Copy the config.template.py into a config.py file in the root directory and update with preferred settings.

For logging to AWS, there needs to be an AWS Lambda function configured with a URL endpoint and a secret token environment variable configured that matches the value in the config.py file.
