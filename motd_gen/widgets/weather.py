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
        show_forecast = self.config.get("show_forecast", True)

        temp_unit = "fahrenheit" if units == "f" else "celsius"
        unit_label = "°F" if units == "f" else "°C"
        wind_unit = "mph" if units == "f" else "km/h"
        precip_unit = "inch" if units == "f" else "mm"

        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,uv_index,cloud_cover,precipitation",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,weather_code",
                "temperature_unit": temp_unit,
                "wind_speed_unit": "mph" if units == "f" else "kmh",
                "precipitation_unit": precip_unit,
                "timezone": "auto",
                "forecast_days": 3,
            }

            response = requests.get(self.API_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            current = data["current"]
            daily = data["daily"]

            temp = current["temperature_2m"]
            feels = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            wind_dir = self._wind_direction(current["wind_direction_10m"])
            weather_code = current["weather_code"]
            pressure = current["pressure_msl"]
            uv = current["uv_index"]
            cloud_cover = current["cloud_cover"]
            precip = current["precipitation"]

            desc = WMO_CODES.get(weather_code, "Unknown")

            # Sunrise/sunset for today
            sunrise = daily["sunrise"][0].split("T")[1] if daily["sunrise"][0] else "N/A"
            sunset = daily["sunset"][0].split("T")[1] if daily["sunset"][0] else "N/A"

            lines = [
                f"{label}:",
                f"  {desc}, {temp:.0f}{unit_label} (feels {feels:.0f}{unit_label})",
                f"  Humidity: {humidity}% | Wind: {wind:.0f} {wind_unit} {wind_dir} | Cloud Cover: {cloud_cover}%",
                f"  Pressure: {pressure:.0f} hPa | UV Index: {uv:.1f} | Precip: {precip:.2f} {precip_unit}",
                f"  Sunrise: {sunrise} | Sunset: {sunset}",
            ]

            if show_forecast:
                lines.append("")
                lines.append("  Forecast:")

                from datetime import datetime
                day_names = ["Today", "Tomorrow"]
                for i in range(min(3, len(daily["time"]))):
                    if i < len(day_names):
                        day_label = day_names[i]
                    else:
                        date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                        day_label = date.strftime("%A")
                    high = daily["temperature_2m_max"][i]
                    low = daily["temperature_2m_min"][i]
                    rain_chance = daily["precipitation_probability_max"][i]
                    day_code = daily["weather_code"][i]
                    day_desc = WMO_CODES.get(day_code, "Unknown")
                    lines.append(
                        f"    {day_label:<10} {day_desc:<18} H: {high:.0f}{unit_label}  L: {low:.0f}{unit_label}  Rain: {rain_chance}%"
                    )

            return lines

        except requests.ConnectionError:
            return [f"{label}: no internet connection"]
        except requests.Timeout:
            return [f"{label}: request timed out"]
        except Exception as e:
            return [f"{label}: unavailable ({e})"]

    def _wind_direction(self, degrees: float) -> str:
        """Convert wind degrees to compass direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                       "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]