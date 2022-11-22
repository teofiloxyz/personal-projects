#!/usr/bin/python3

import subprocess


class Weather:
    def __init__(self):
        self.info_cache_path = "?"
        self.load_cache()

    def load_cache(self):
        with open(self.info_cache_path, "rb") as wc:
            (
                self.current_weather_info,
                self.forecast_weather_info,
                self.weather_alerts,
            ) = pickle.load(wc)

    def show(self, mode, show_alerts=False):
        # Could use some refactoring
        cw, fw = self.current_weather_info, self.forecast_weather_info
        if mode == "essential":
            print("DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tCLD%\tUV")
            for n, day in enumerate(fw, 1):
                print(
                    f'{day["week_day"][:3]},{day["date"][-2:]}\t'
                    f'{day["max_temp"]}º\t{day["min_temp"]}º\t'
                    f'{day["rain_prob"]}\t{day["rain_size"]}\t'
                    f'{day["wind_spd"]}\t'
                    f'{day["cld_prctg"]}\t{day["uv_index"]}\t'
                )
                if n == 7:
                    break
            print(
                f'\nCurrent temperature: {cw["curr_temp"]}º '
                f'({cw["curr_ftemp"]}º felt)\nLast update: '
                f'{cw["last_update"]} ({cw["location"]})'
            )
        else:
            print(
                "DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tHUM%\tCLD%\tUV\tSUNRISE"
                "\t\tSUNSET\t\tDESCRIPTION"
            )
            for day in fw:
                print(
                    f'{day["week_day"][:3]},{day["date"][-2:]}\t'
                    f'{day["max_temp"]}º\t{day["min_temp"]}º\t'
                    f'{day["rain_prob"]}\t{day["rain_size"]}\t'
                    f'{day["wind_spd"]}\t{day["hmd_prctg"]}\t'
                    f'{day["cld_prctg"]}\t{day["uv_index"]}\t'
                    f'{day["sunrise"]}\t{day["sunset"]}\t\t{day["weather"]}'
                )
            print(
                f'\nCurrent temperature: {cw["curr_temp"]}º '
                f'({cw["curr_ftemp"]}º felt)\nLast update: '
                f'{cw["last_update"]} ({cw["location"]})'
            )

        if show_alerts:
            self.show_weather_alerts()

    def refresh(self):
        Update_Cache().main()
        self.load_cache()
        self.show("essential", show_alerts=True)

    def show_weather_alerts(self):
        self.load_cache()

        if len(self.weather_alerts) == 0:
            print("No weather alerts.")
            return

        [print(alert) for alert in self.weather_alerts]

    @staticmethod
    def beachcam():
        subprocess.Popen("wmctrl -s 1", shell=True)
        url = '"https://beachcam.meo.pt/livecams/?"'
        cmd = "firefox --new-tab --url " + url
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        exit()

    @staticmethod
    def ipma():
        subprocess.Popen("wmctrl -s 1", shell=True)
        url = '"https://www.ipma.pt/en/otempo/prev.localidade.hora/#'
        place = '?"'
        cmd = "firefox --new-tab --url " + url + place
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        exit()
