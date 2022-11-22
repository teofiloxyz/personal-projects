#!/usr/bin/python3
"""Public-APIs: https://github.com/public-apis/public-apis
Script API docs:
https://www.weatherbit.io/api/weather-forecast-minutely
https://www.weatherbit.io/api/weather-forecast-16-day
https://www.weatherbit.io/api/alerts
https://www.weatherbit.io/api/weather-current"""

import json
import pickle
import requests
from datetime import datetime


class API:
    def __init__(self):
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

    def update_cache(self):
        self.get_info()
        self.select_info()
        self.update_cache_file()

    def get_info(self):
        current_weather_data = requests.get(self.current_weather_url).text
        self.current_weather_data = json.loads(current_weather_data)["data"][0]
        self.weather_alerts = json.loads(current_weather_data)["alerts"]
        forecast_weather_data = requests.get(self.forecast_weather_url).text
        self.forecast_weather_data = json.loads(forecast_weather_data)["data"]

    def select_info(self):
        self.current_weather_info, self.forecast_weather_info = {}, []

        self.current_weather_info["last_update"] = self.current_weather_data[
            "ob_time"
        ]
        self.current_weather_info["location"] = self.current_weather_data[
            "city_name"
        ]
        self.current_weather_info["curr_temp"] = self.current_weather_data[
            "temp"
        ]
        self.current_weather_info["curr_ftemp"] = self.current_weather_data[
            "app_temp"
        ]

        for day in self.forecast_weather_data:
            entry = {}
            entry["date"] = day["valid_date"]
            date = datetime.strptime(day["valid_date"], "%Y-%m-%d")
            entry["week_day"] = datetime.strftime(date, "%A")
            entry["weather"] = day["weather"]["description"]
            entry["max_temp"] = day["max_temp"]
            entry["min_temp"] = day["min_temp"]
            entry["rain_prob"] = day["pop"]
            entry["rain_size"] = round(day["precip"], 2)
            entry["wind_spd"] = day["wind_spd"]
            entry["hmd_prctg"] = day["rh"]
            entry["cld_prctg"] = day["clouds"]
            entry["uv_index"] = day["uv"]
            sunrise = day["sunrise_ts"]
            entry["sunrise"] = datetime.fromtimestamp(sunrise).strftime(
                "%H:%M:%S"
            )
            sunset = day["sunset_ts"]
            entry["sunset"] = datetime.fromtimestamp(sunset).strftime(
                "%H:%M:%S"
            )
            self.forecast_weather_info.append(entry)

    def update_cache_file(self):
        with open(self.weather_cache_path, "wb") as wc:
            pickle.dump(
                [
                    self.current_weather_info,
                    self.forecast_weather_info,
                    self.weather_alerts,
                ],
                wc,
            )
