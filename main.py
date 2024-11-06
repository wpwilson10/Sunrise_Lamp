import network
import urequests
import machine
import ntptime
import time

# WiFi credentials
SSID: str = "xxxxxxxx"
PASSWORD: str = "yyyyyyyyy"

# CURRENT LOCATION
LATITUDE: float = 89.123
LONGITUDE: float = -89.987

# Schedule times - as number of seconds since midnight
UPDATE_TIME: int = 14400  # 4:00 AM
SUNRISE_TIME: int = 25200  # 7:00 AM
DAYTIME_TIME: int = 27000  # 7:30 AM
SUNSET_TIME: int = (
    70200  # 7:30 PM or local sunset time as calculated in update_sunset_time()
)
BED_TIME: int = 82800  # 11:00 PM

# Time corrections - will be set by update_current_time
TIMEZONE_OFFSET: int = (
    0  # number of seconds to add/subtract from UTC to get central time
)
DST_OFFSET: int = (
    0  # number of seconds to add/substract to correct for daylight savings
)

# Constants
FREQUENCY: int = (
    8000  # 8 kHz frequency. 3 kHz = IEEE 1789 standard recommmended frequency for no human perception
)
MAX_DUTY_CYCLE: int = 65535  # number of duty cycle levels available to Pi Pico
WARM_LED_PIN: int = 10  # GPIO
COOL_LED_PIN: int = 20  # GPIO

# Setup Outputs and PWMs globally
warm = machine.PWM(machine.Pin(WARM_LED_PIN))
warm.freq(FREQUENCY)

cool = machine.PWM(machine.Pin(COOL_LED_PIN))
cool.freq(FREQUENCY)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Network connected!")
    print("IP Address:", wlan.ifconfig()[0])


def get_manual_settings():
    # Checks if there are manual settings setup configured on the remote server
    # See the project directory on PatrickSR0 under Projects/LampServer for more info

    try:
        # Replace with the URL of your local file
        url = "http://localhost:8089/settings.txt"

        # Fetch the file
        response = urequests.get(url)
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

        global TIMEZONE_OFFSET
        global DST_OFFSET

        TIMEZONE_OFFSET = data["raw_offset"]  # timezone correction
        DST_OFFSET = data["dst_offset"]  # daylight savings correction

        print("UTC:", time.time())
        print("TZ Offset:", TIMEZONE_OFFSET)
        print("DST Offset:", DST_OFFSET)
    except Exception as e:
        print("Failed to fetch or parse time from API:", e)


def update_sunset_time():
    # Uses internet APIs to set the sunset time in seconds since midnight
    # for the current local and local time. Will always return 7:30 PM
    # at the earliest, or actual sunset time when it is later

    # Construct the API URL with timezone and formatted parameter
    url = f"https://api.sunrise-sunset.org/json?lat={LATITUDE}&lng={LONGITUDE}&tzid=America/Chicago&formatted=0"

    # Make the API request using urequests
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

        global SUNSET_TIME
        SUNSET_TIME = max(70200, sunset_seconds)  # 7:30 PM or later
        print("Real Sunset time:", sunset_seconds)
        print("SUNSET_TIME:", SUNSET_TIME)
    else:
        print("Failed to fetch or parse time from api.sunrise-sunset.org.")


def seconds_since_midnight() -> int:
    # Calculates number of seconds since midnight for the local time
    # using previously set RTC and corrections

    corrected_time = time.time() + TIMEZONE_OFFSET + DST_OFFSET
    local_time = time.localtime(corrected_time)
    seconds_since_midnight = local_time[3] * 3600 + local_time[4] * 60 + local_time[5]
    print(f"Current time in seconds since midnight: {seconds_since_midnight}")

    return seconds_since_midnight


def get_duty_for_brightness(v_out: float) -> int:
    # For a given desired perceived brightness percentage (0.00 - 1.00 e.g. 0.25 for 25%)
    # Returns the duty cycle required

    v_in: float = (
        v_out**2.2
    )  # https://codeinsecurity.wordpress.com/2023/07/17/the-problem-with-driving-leds-with-pwm/

    return round(MAX_DUTY_CYCLE * v_in)


def night_light():
    # 11:30PM - 6AM, night light mode - dim warm light
    # No times
    print("NIGHTLIGHT")
    warm.duty_u16(get_duty_for_brightness(0.25))  # Warm at 25% brightness
    cool.duty_u16(0)  # Cool off


def sunrise():
    # 7 AM, sunrise - warm lights increase brightness.
    # 30 minute cycle

    # Start from night light settings
    cool.duty_u16(0)  # Cool off
    warm.duty_u16(get_duty_for_brightness(0.25))  # Warm at 25% brightness
    print("SUNRISE")

    time.sleep(diff_time(SUNRISE_TIME))

    for brightness in range(250, 1000, 1):
        # gradual brighten warm light
        warm.duty_u16(get_duty_for_brightness(brightness / 1000))
        time.sleep(2.4)  # 2.4 seconds * 750 steps = 30 minutes


def daylight():
    # 7:30 AM, Day time - full brightness
    # 30 minute cycle

    # Start at full warm brightness
    cool.duty_u16(0)  # Cool off
    warm.duty_u16(get_duty_for_brightness(1))
    print("DAYLIGHT")

    time.sleep(diff_time(DAYTIME_TIME))

    for brightness in range(1000):
        # Cool lights brighten to max brightness
        cool.duty_u16(get_duty_for_brightness(brightness / 1000))
        # Warm dim to 75% brightness = ~50% power
        warm.duty_u16(get_duty_for_brightness(max(0.75, (1000 - brightness) / 1000)))
        time.sleep(1.8)  # 1.8 seconds * 1000 steps = 30 minutes


def sunset():
    # 7:30 PM, Sunset - Warm light only

    # Setting brightness is reduant when scheduled routines are running
    # as they will have already set the correct brightness
    # But this is nice when restarting during the day
    warm.duty_u16(get_duty_for_brightness(0.75))  # Warm at 75% brightness
    cool.duty_u16(get_duty_for_brightness(1))  # Cool at 100% brightness
    print("SUNSET")

    time.sleep(diff_time(SUNSET_TIME))

    # 30 minute cycle
    for brightness in range(1000):
        # Cool lights dim to 0 brightness
        cool.duty_u16(get_duty_for_brightness((1000 - brightness) / 1000))
        # Warm lights brighten to 100% brightness
        warm.duty_u16(get_duty_for_brightness(max(0.75, brightness / 1000)))
        time.sleep(1.8)  # 1.8 seconds * 1000 steps = 30 minutes


def bed_time():
    # 11 PM, Dim to night light
    # 30 minute cycle

    # Setting brightness is reduant when scheduled routines are running
    # as they will have already set the correct brightness
    # But this is nice when restarting during the evening
    warm.duty_u16(get_duty_for_brightness(1))
    cool.duty_u16(0)  # Cool off
    print("BEDTIME")

    time.sleep(diff_time(BED_TIME))

    for brightness in range(1000, 250, -1):
        # Warm dims to 25% brightness
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

    if diff_time(UPDATE_TIME):
        # If before 4 AM, wait until 4 AM, then update local time
        night_light()  # start at dim setting
        time.sleep(diff_time(UPDATE_TIME))
        update_current_time()
        update_sunset_time()

    elif diff_time(SUNRISE_TIME):
        # 6:30 AM, sunrise
        sunrise()

    elif diff_time(DAYTIME_TIME):
        # 7:30 AM, Day time
        daylight()

    elif diff_time(SUNSET_TIME):
        # 7:30 PM or later based on local time, Sunset
        sunset()

    elif diff_time(BED_TIME):
        # 11:00 PM, Bed time
        bed_time()

    else:
        # default, night light mode then wait a bit
        night_light()
        time.sleep(720)


try:
    # start at dim setting
    night_light()

    # Connect to WiFi
    connect_wifi()

    # If there are manual override settings, use them
    get_manual_settings()

    # Initial time fetch and calculations
    update_current_time()
    update_sunset_time()

    # Schedule the timer to check every 60000 milliseconds (1 minute) and run appropriate day/night routine
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
