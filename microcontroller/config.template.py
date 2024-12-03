# WiFi Credentials
# SSID (network name) of the WiFi network to connect to.
WIFI_SSID = "wifi_name"
# Password for the WiFi network.
WIFI_PASSWORD = "wifi_password"

# Latitude of the device's location, used for scheduling events based on local time.
LATITUDE = 89.123
# Longitude of the device's location.
LONGITUDE = -89.987

# Schedule Times (in seconds since midnight)
# Time of day to update the system, such as refreshing sunrise/sunset times.
UPDATE_TIME = 14400  # 4:00 AM
# Time of day to start "daytime" mode, typically the local sunrise time.
SUNRISE_TIME = 25200  # 7:00 AM
# Time to fully enter daytime mode (i.e., full light brightness).
DAYTIME_TIME = 27000  # 7:30 AM
# Time of day to start "nighttime" mode, typically the local sunset time.
SUNSET_TIME = 70200  # 7:30 PM
# Time of day to enter sleep mode.
BED_TIME = 82800  # 11:00 PM

# Time Corrections
# Offset from UTC in seconds to adjust to the local timezone.
# This can be automatically updated by the application
TIMEZONE_OFFSET = 0
# Additional offset in seconds to account for daylight savings time
# This can be automatically updated by the application
DST_OFFSET = 0

# PWM Settings
# Frequency in Hz, used for configuring hardware PWM.
PWM_FREQUENCY = 8000  # Based on IEEE 1789 * 2 Safety Factor
# Maximum duty cycle level for PWM, defines the range of light brightness levels.
MAX_DUTY_CYCLE = 65535  # Max duty cycle level for Pi Pico W
# GPIO pin for the warm LED.
WARM_LED_PIN = 10  # PWM enabled pin on Pi Pico W
# GPIO pin for the cool LED.
COOL_LED_PIN = 20  # PWM enabled pin on Pi Pico W

# AWS
# Address of the lambda function endpoint for posting logs
AWS_LOG_URL = "https://xyz.lambda-url.us-east-1.on.aws/"
# Shared secret token for authenticating access to endpoint
AWS_SECRET_TOKEN = "my_secure_static_token_12345"
