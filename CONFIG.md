# Configuration Documentation

This file documents the configuration settings used in `config.json`.

## WIFI CREDENTIALS

-   **`WIFI.SSID`**: The SSID (network name) of the WiFi network to connect to.
-   **`WIFI.PASSWORD`**: The password for the WiFi network.

## URLS

-   **`URL.LOCAL_SETTINGS`**: The address of the local server hosting manual override settings.

## LOCATION

-   **`LOCATION.LATITUDE`**: Latitude of the device's location, used for scheduling events based on local time.
-   **`LOCATION.LONGITUDE`**: Longitude of the device's location.

## SCHEDULE TIMES (in seconds since midnight)

-   **`SCHEDULE_TIMES.UPDATE_TIME`**: Time of day to update the system, such as refreshing sunrise/sunset times (e.g., 14400 for 4:00 AM).
-   **`SCHEDULE_TIMES.SUNRISE_TIME`**: Time of day to start "daytime" mode, typically the local sunrise time.
-   **`SCHEDULE_TIMES.DAYTIME_TIME`**: Time to fully enter daytime mode (e.g., full light brightness).
-   **`SCHEDULE_TIMES.SUNSET_TIME`**: Time of day to start "nighttime" mode, typically the local sunset time.
-   **`SCHEDULE_TIMES.BED_TIME`**: Time of day to enter sleep mode.

## TIME CORRECTIONS

-   **`TIME_CORRECTIONS.TIMEZONE_OFFSET`**: Offset from UTC in seconds to adjust to the local timezone.
-   **`TIME_CORRECTIONS.DST_OFFSET`**: Additional offset to account for daylight savings time, if applicable.

## PWM SETTINGS

-   **`PWM.FREQUENCY`**: Frequency in Hz, used for setting PWM or other timing-related parameters.
-   **`PWM.MAX_DUTY_CYCLE`**: Maximum duty cycle level.
-   **`PWM.WARM_LED_PIN`**: GPIO pin for the warm LED.
-   **`PWM.COOL_LED_PIN`**: GPIO pin for the cool LED.

---

### Example `config.json`

```jsonc
{
	"WIFI": {
		"SSID": "xxxxxxxx", // WiFi network name
		"PASSWORD": "yyyyyyyyy" // WiFi password
	},
	"URL": {
		"LOCAL_SETTINGS": "http://localhost:8089/settings.txt" // where to find manual override settings
	},
	"LOCATION": {
		"LATITUDE": 89.123, // Latitude for location-based scheduling
		"LONGITUDE": -89.987 // Longitude for location-based scheduling
	},
	"SCHEDULE_TIMES": {
		"UPDATE_TIME": 14400, // 4:00 AM update time
		"SUNRISE_TIME": 25200, // 7:00 AM
		"DAYTIME_TIME": 27000, // 7:30 AM
		"SUNSET_TIME": 70200, // 7:30 PM
		"BED_TIME": 82800 // 11:00 PM
	},
	"TIME_CORRECTIONS": {
		"TIMEZONE_OFFSET": 0, // Timezone offset from UTC
		"DST_OFFSET": 0 // Daylight savings adjustment
	},
	"PWM": {
		"FREQUENCY": 8000, // PWM frequency in Hz
		// 3 kHz = IEEE 1789 standard recommended frequency for no human perception
		"MAX_DUTY_CYCLE": 65535, // number of duty cycle levels available to Pi Pico
		"WARM_LED_PIN": 10, // PWM enabled pin on Pi Pico W
		"COOL_LED_PIN": 20 // PWM enabled pin on Pi Pico W
	}
}
```
