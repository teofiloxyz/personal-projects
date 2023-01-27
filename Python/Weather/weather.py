import pickle
import subprocess
from enum import Enum, auto

from api import API, CurrentWeather, ForecastWeather


class ShowMode(Enum):
    ALL = auto()
    ESSENTIAL = auto()


class Weather:
    def __init__(self) -> None:
        self.info_cache_path = "?"
        self._load_cache()

    def _load_cache(self) -> None:
        with open(self.info_cache_path, "rb") as wc:
            (self.weather_cache,) = pickle.load(wc)

    def show(self, show_mode: ShowMode) -> None:
        current_weather = self.weather_cache.current_weather
        forecast_weather = self.weather_cache.forecast_weather

        self._print_header(show_mode)
        if show_mode == ShowMode.ESSENTIAL:
            self._print_forecast_weather(forecast_weather, show_mode)
        else:
            self._print_forecast_weather(forecast_weather, show_mode)
        self._print_current_weather(current_weather)

    def _print_header(self, show_mode: ShowMode) -> None:
        if show_mode == ShowMode.ESSENTIAL:
            print("DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tCLD%\tUV")
        else:
            print(
                "DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tHUM%\tCLD%\tUV\t"
                "SUNRISE\t\tSUNSET\t\tDESCRIPTION"
            )

    def _print_forecast_weather(
        self, forecast_weather: list[ForecastWeather], show_mode: ShowMode
    ) -> None:
        n = 7 if show_mode == ShowMode.ESSENTIAL else None
        for day in forecast_weather[:n]:
            print(
                f"{day.date}\t{day.max_temp}º\t{day.min_temp}º\t"
                f"{day.rain_prob}\t{day.rain_size}\t{day.wind_spd}\t"
                f"{day.hmd_prctg}\t{day.cld_prctg}\t{day.uv_index}\t"
            )
            if show_mode == ShowMode.ESSENTIAL:
                continue
            print(f"{day.sunrise}\t{day.sunset}\t\t{day.weather}")

    def _print_current_weather(self, current_weather: CurrentWeather) -> None:
        print(
            f"\nCurrent temperature: {current_weather.curr_temp}º "
            f"({current_weather.curr_ftemp}º felt)\nLast update: "
            f"{current_weather.last_update} ({current_weather.location})"
        )

    def refresh(self) -> None:
        API().update_cache()
        self._load_cache()
        self.show(ShowMode.ESSENTIAL)

    def show_weather_alerts(self) -> None:
        self._load_cache()
        weather_alerts = self.weather_cache.current_weather.weather_alerts

        if len(weather_alerts) == 0:
            print("No weather alerts.")
            return

        [print(alert) for alert in weather_alerts]

    def beachcam(self) -> None:
        url = '"https://beachcam.meo.pt/livecams/?"'
        self._open_url_on_browser(url)
        exit()

    def ipma(self) -> None:
        url = '"https://www.ipma.pt/en/otempo/prev.localidade.hora/#?'
        self._open_url_on_browser(url)
        exit()

    def _open_url_on_browser(self, url: str) -> None:
        cmd = "firefox --new-tab --url " + url
        subprocess.Popen(cmd, shell=True, start_new_session=True)
