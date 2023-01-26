"""Public-APIs: https://github.com/public-apis/public-apis
Script API docs:
https://www.weatherbit.io/api/weather-forecast-minutely
https://www.weatherbit.io/api/weather-forecast-16-day
https://www.weatherbit.io/api/alerts
https://www.weatherbit.io/api/weather-current"""

import json
import pickle
import requests
from dataclasses import dataclass


@dataclass
class CurrentWeather:
    last_update: str
    location: str
    curr_temp: float
    curr_ftemp: float
    alerts: str


@dataclass
class ForecastWeather:
    date: str
    weather: str
    max_temp: float
    min_temp: float
    rain_prob: float
    rain_size: float
    wind_spd: float
    hmd_prctg: float
    cld_prctg: float
    uv_index: float
    sunrise: str
    sunset: str


@dataclass
class WeatherCache:
    current_weather: CurrentWeather
    forecast_weather: list[ForecastWeather]


class API:
    def __init__(self) -> None:
        self.weather_cache_path = "?"
        local_lat, local_lon = "?", "?"
        api_key = "?"
        self.current_weather_url = (
            "https://api.weatherbit.io/v2.0/current?"
            f"lat={local_lat}&lon={local_lon}&key={api_key}&include=alerts"
        )
        self.forecast_weather_url = (
            "https://api.weatherbit.io/v2.0/forecast"
            f"/daily?lat={local_lat}&lon={local_lon}&key={api_key}"
        )

    def update_cache(self) -> None:
        self._get_info()
        weather_cache = self._select_info()
        self._update_file(weather_cache)

    def _get_info(self) -> None:
        current_weather_data = requests.get(self.current_weather_url).text
        forecast_weather_data = requests.get(self.forecast_weather_url).text

        self.current_weather_data = json.loads(current_weather_data)["data"][0]
        self.weather_alerts = json.loads(current_weather_data)["alerts"]
        self.forecast_weather_data = json.loads(forecast_weather_data)["data"]

    def _select_info(self) -> WeatherCache:
        current_weather = self._get_current_weather()
        forecast_weather = [
            self._get_forecast_weather(day)
            for day in self.forecast_weather_data
        ]
        return WeatherCache(current_weather, forecast_weather)

    def _get_current_weather(self) -> CurrentWeather:
        return CurrentWeather(
            last_update=self.current_weather_data["ob_time"],
            location=self.current_weather_data["city_name"],
            curr_temp=self.current_weather_data["temp"],
            curr_ftemp=self.current_weather_data["app_temp"],
            alerts=self.weather_alerts,
        )

    def _get_forecast_weather(self, day: dict) -> ForecastWeather:
        return ForecastWeather(
            date=day["valid_date"],
            weather=day["weather"]["description"],
            max_temp=day["max_temp"],
            min_temp=day["min_temp"],
            rain_prob=day["pop"],
            rain_size=round(day["precip"], 2),
            wind_spd=day["wind_spd"],
            hmd_prctg=day["rh"],
            cld_prctg=day["clouds"],
            uv_index=day["uv"],
            sunrise=day["sunrise_ts"],
            sunset=day["sunset_ts"],
        )

    def _update_file(self, weather_cache: WeatherCache) -> None:
        with open(self.weather_cache_path, "wb") as wc:
            pickle.dump(weather_cache, wc)
