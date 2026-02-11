"""Weather widget using Open-Meteo API."""

import requests
from motd_gen.widgets.base import BaseWidget

# WMO Weather Interpretation Codes
# https://open-meteo.com/en/docs
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherWidget(BaseWidget):
    """Displays current weather using Open-Meteo API."""

    API_URL = "https://api.open-meteo.com/v1/forecast"

    @property
    def name(self) -> str:
        return "weather"

    def render(self) -> list[str]:
        """Fetch weather data and format a compact summary."""
        latitude = self.config.get("latitude", 0)
        longitude = self.config.get("longitude", 0)
        units = self.config.get("units", "f")
        timeout = self.config.get("timeout", 5)
        label = self.config.get("label", "Weather")

        temp_unit = "fahrenheit" if units == "f" else "celsius"
        unit_label = "°F" if units == "f" else "°C"

        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "temperature_unit": temp_unit,
                "wind_speed_unit": "mph" if units == "f" else "kmh",
            }

            response = requests.get(self.API_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            current = data["current"]
            temp = current["temperature_2m"]
            feels = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            weather_code = current["weather_code"]
            wind_unit = "mph" if units == "f" else "km/h"

            desc = WMO_CODES.get(weather_code, "Unknown")

            return [
                f"{label}:",
                f"  {desc}, {temp:.0f}{unit_label} (feels {feels:.0f}{unit_label})",
                f"  Humidity: {humidity}% | Wind: {wind:.0f} {wind_unit}",
            ]

        except requests.ConnectionError:
            return [f"{label}: no internet connection"]
        except requests.Timeout:
            return [f"{label}: request timed out"]
        except Exception as e:
            return [f"{label}: unavailable ({e})"]
