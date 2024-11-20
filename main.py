import network
import urequests
import machine
import ntptime
import time
import config

# Setup Outputs and PWMs globally
warm = machine.PWM(machine.Pin(config.WARM_LED_PIN))
warm.freq(config.PWM_FREQUENCY)

cool = machine.PWM(machine.Pin(config.COOL_LED_PIN))
cool.freq(config.PWM_FREQUENCY)

# These values can be overridden, so pull out into separate values
SUNSET_TIME_CALCULATED = config.SUNSET_TIME
TIMEZONE_OFFSET_CALCULATED = config.TIMEZONE_OFFSET
DST_OFFSET_CALCULATED = config.DST_OFFSET


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print("Network connected!")
    print("IP Address:", wlan.ifconfig()[0])


def post_log_aws(message: str):
    # Sends the given string to an AWS Lambda endpoint
    #   which then saves the message to CloudWatch Logs

    # Define Lambda URL and pre-shared token
    headers = {
        "Content-Type": "application/json",
        "X-Custom-Auth": config.AWS_SECRET_TOKEN,  # Pre-shared token
    }

    # Prepare log data
    log_data = {"message": message}

    # Send log data
    response = urequests.post(config.AWS_LOG_URL, json=log_data, headers=headers)
    print("Response:", response.text)
    response.close()


def get_manual_settings():
    # Checks if there are manual settings setup configured on the remote server
    # See the project directory on PatrickSR0 under Projects/LampServer for more info

    try:
        response = urequests.get(config.LOCAL_SETTINGS_URL)
        data = str(response.text)
        response.close()

        if response.status_code == 200:
            print("File found! Contents:")
            print(data)
        else:
            print(f"Failed to retrieve file, status code: {response.status_code}")
            return

        data = data.strip()

        if len(data) == 0 or "-1,-1" in data:
            # empty or default settings, run normal program
            return
        else:
            # if manual settings exist, use them for next 12 hours
            data = data.split(",")
            cool_override, warm_override = float(data[0]), float(data[1])

            cool.duty_u16(get_duty_for_brightness(float(cool_override)))
            warm.duty_u16(get_duty_for_brightness(float(warm_override)))
            print(f"Manual: Cool = {cool_override}, Warm = {warm_override}")

            time.sleep(12 * 60 * 60)  # sleep 12 hours

    except Exception as e:
        print("Failed to fetch override settings from local server:", e)


def update_current_time():
    # Uses internet APIs to set the RTC to unix time
    # and set the timezone and daylight savings offsets

    try:
        # sets the RTC with the unix epoch from the internet
        ntptime.settime()

        # get the timezone and daylight savings offsets from another API
        # https://worldtimeapi.org/pages/schema
        response = urequests.get(
            "https://worldtimeapi.org/api/timezone/America/Chicago"
        )
        data = response.json()
        response.close()

        TIMEZONE_OFFSET_CALCULATED = data["raw_offset"]
        DST_OFFSET_CALCULATED = data["dst_offset"]

        print("UTC:", time.time())
        print("TZ Offset:", TIMEZONE_OFFSET_CALCULATED)
        print("DST Offset:", DST_OFFSET_CALCULATED)
    except Exception as e:
        print("Failed to fetch or parse time from API:", e)


def update_sunset_time():
    # Uses internet APIs to set the sunset time in seconds since midnight
    # for the current local and local time. Will always return 7:30 PM
    # at the earliest, or actual sunset time when it is later

    # Construct the API URL with timezone and formatted parameter
    url = (
        f"https://api.sunrise-sunset.org/json?lat={config.LATITUDE}"
        f"&lng={config.LONGITUDE}&tzid=America/Chicago&formatted=0"
    )

    response = urequests.get(url)
    data = response.json()
    response.close()

    if data["status"] == "OK":
        # Extract sunset time from the response
        sunset_time = data["results"]["sunset"]
        # The time format is "HH:MM:SS AM/PM", we need to convert this to seconds since midnight

        # Parsing time, remove timezone part if there
        time_part = sunset_time.split("T")[1]
        time_str = time_part.split("-")[0]  # Remove the timezone offset "-05:00"
        time_str = time_str.split("+")[
            0
        ]  # Safety check in case of a '+' timezone offset

        # Splitting the time into components
        hours, minutes, seconds = map(int, time_str.split(":"))

        # Calculate total seconds since midnight
        sunset_seconds = hours * 3600 + minutes * 60 + seconds

        SUNSET_TIME_CALCULATED = max(config.SUNSET_TIME, sunset_seconds)
        print("Real Sunset time:", sunset_seconds)
        print("SUNSET_TIME:", SUNSET_TIME_CALCULATED)
    else:
        print("Failed to fetch or parse time from api.sunrise-sunset.org.")


def seconds_since_midnight() -> int:
    # Calculates number of seconds since midnight for the local time
    # using previously set RTC and corrections

    corrected_time = time.time() + TIMEZONE_OFFSET_CALCULATED + DST_OFFSET_CALCULATED
    local_time = time.localtime(corrected_time)
    seconds_since_midnight = local_time[3] * 3600 + local_time[4] * 60 + local_time[5]
    print(f"Current time in seconds since midnight: {seconds_since_midnight}")

    return seconds_since_midnight


def get_duty_for_brightness(v_out: float) -> int:
    # Returns the duty cycle required for a given desired
    #   perceived brightness percentage (0.00 - 1.00 e.g. 0.25 for 25%)
    # Based on https://codeinsecurity.wordpress.com/2023/07/17/the-problem-with-driving-leds-with-pwm/

    return round(config.MAX_DUTY_CYCLE * v_out**2.2)


def night_light():
    # Dim warm light
    print("NIGHTLIGHT")
    warm.duty_u16(get_duty_for_brightness(0.25))
    cool.duty_u16(0)


def sunrise():
    # Warm lights increase to full warm brightness.
    # 30 minute cycle

    # Start from night light settings
    cool.duty_u16(0)
    warm.duty_u16(get_duty_for_brightness(0.25))
    print("SUNRISE")

    time.sleep(diff_time(config.SUNRISE_TIME))

    for brightness in range(250, 1000, 1):
        warm.duty_u16(get_duty_for_brightness(brightness / 1000))
        time.sleep(2.4)  # 2.4 seconds * 750 steps = 30 minutes


def daylight():
    # Switch to cooler light and full combined brightness
    # 30 minute cycle

    cool.duty_u16(0)
    warm.duty_u16(get_duty_for_brightness(1))
    print("DAYLIGHT")

    time.sleep(diff_time(config.DAYTIME_TIME))

    for brightness in range(1000):
        cool.duty_u16(get_duty_for_brightness(brightness / 1000))
        warm.duty_u16(get_duty_for_brightness(max(0.75, (1000 - brightness) / 1000)))
        time.sleep(1.8)  # 1.8 seconds * 1000 steps = 30 minutes


def sunset():
    # Transition to warm light only

    # Setting brightness is reduant when scheduled routines are running
    # as they will have already set the correct brightness
    # But this is nice when restarting during the day
    warm.duty_u16(get_duty_for_brightness(0.75))
    cool.duty_u16(get_duty_for_brightness(1))
    print("SUNSET")

    # use the updated sunset time
    time.sleep(diff_time(SUNSET_TIME_CALCULATED))

    for brightness in range(1000):
        cool.duty_u16(get_duty_for_brightness((1000 - brightness) / 1000))
        warm.duty_u16(get_duty_for_brightness(max(0.75, brightness / 1000)))
        time.sleep(1.8)  # 1.8 seconds * 1000 steps = 30 minutes


def bed_time():
    # Dim to night light
    # 30 minute cycle

    # Setting brightness is reduant when scheduled routines are running
    # as they will have already set the correct brightness
    # But this is nice when restarting during the evening
    warm.duty_u16(get_duty_for_brightness(1))
    cool.duty_u16(0)
    print("BEDTIME")

    time.sleep(diff_time(config.BED_TIME))

    for brightness in range(1000, 250, -1):
        warm.duty_u16(get_duty_for_brightness(brightness / 1000))
        time.sleep(2.4)  # 2.4 seconds * 750 = 30 minutes


def diff_time(ref_time: int) -> int:
    # Returns the number of seconds between now and the reference time,
    # Or 0 if it would be negative
    return max(0, ref_time - seconds_since_midnight())


def run_scheduled_tasks():
    # Checks what the next day/night lighting cycle step will be and runs that routine.
    # Each routine has logic to wait until the correct time before starting after being called.
    # Run on startup and using a scheduled timer

    if diff_time(config.UPDATE_TIME):
        night_light()
        time.sleep(diff_time(config.UPDATE_TIME))
        update_current_time()
        update_sunset_time()

    elif diff_time(config.SUNRISE_TIME):
        sunrise()

    elif diff_time(config.DAYTIME_TIME):
        daylight()

    elif diff_time(SUNSET_TIME_CALCULATED):
        sunset()

    elif diff_time(config.BED_TIME):
        bed_time()

    else:
        night_light()
        time.sleep(720)


try:
    night_light()  # start at dim setting
    connect_wifi()
    # If there are manual override settings, use them
    get_manual_settings()
    # Initial time fetch and calculations
    update_current_time()
    update_sunset_time()

    # Schedule the timer to check every 60000 milliseconds (1 minute)
    #   and run appropriate day/night routine
    timer = machine.Timer()
    timer.init(
        period=60000,
        mode=machine.Timer.PERIODIC,
        callback=lambda t: run_scheduled_tasks(),
    )

    # start lighting cycle
    run_scheduled_tasks()
except KeyboardInterrupt:
    machine.reset()
except Exception as e:
    print("Unknown error:", e)
