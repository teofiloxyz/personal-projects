#!/usr/bin/python3
'''Public-APIs: https://github.com/public-apis/public-apis
Script API docs:
https://www.weatherbit.io/api/weather-forecast-minutely
https://www.weatherbit.io/api/weather-forecast-16-day
https://www.weatherbit.io/api/alerts
https://www.weatherbit.io/api/weather-current'''

import sys
import subprocess
import json
import pickle
import requests
from configparser import ConfigParser
from Tfuncs import gmenu
from datetime import datetime


class Weather:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.weather_cache_path = self.config['GENERAL']['cache_path']
        self.browser = self.config['BROWSER']['browser']
        self.ipma_place = self.config['BROWSER']['ipma_place']
        self.beachcam_url = self.config['BROWSER']['beachcam_url']
        self.load_cache()

    def load_cache(self):
        with open(self.weather_cache_path, 'rb') as wc:
            self.current_weather_info, self.forecast_weather_info, \
                self.weather_alerts = pickle.load(wc)

    def show(self, mode, show_alerts=False):
        # Could use some refactoring
        cw, fw = self.current_weather_info, self.forecast_weather_info
        if mode == 'essential':
            print('DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tCLD%\tUV')
            for n, day in enumerate(fw, 1):
                print(f'{day["week_day"][:3]},{day["date"][-2:]}\t'
                      f'{day["max_temp"]}º\t{day["min_temp"]}º\t'
                      f'{day["rain_prob"]}\t{day["rain_size"]}\t'
                      f'{day["wind_spd"]}\t'
                      f'{day["cld_prctg"]}\t{day["uv_index"]}\t')
                if n == 7:
                    break
            print(f'\nCurrent temperature: {cw["curr_temp"]}º '
                  f'({cw["curr_ftemp"]}º felt)\nLast update: '
                  f'{cw["last_update"]} ({cw["location"]})')
        else:
            print('DAY\tMAX\tMIN\tRAIN%\tRAINº\tWIND\tHUM%\tCLD%\tUV\tSUNRISE'
                  '\t\tSUNSET\t\tDESCRIPTION')
            for day in fw:
                print(f'{day["week_day"][:3]},{day["date"][-2:]}\t'
                      f'{day["max_temp"]}º\t{day["min_temp"]}º\t'
                      f'{day["rain_prob"]}\t{day["rain_size"]}\t'
                      f'{day["wind_spd"]}\t{day["hmd_prctg"]}\t'
                      f'{day["cld_prctg"]}\t{day["uv_index"]}\t'
                      f'{day["sunrise"]}\t{day["sunset"]}\t\t{day["weather"]}')
            print(f'\nCurrent temperature: {cw["curr_temp"]}º '
                  f'({cw["curr_ftemp"]}º felt)\nLast update: '
                  f'{cw["last_update"]} ({cw["location"]})')

        if show_alerts:
            self.show_weather_alerts()

    def refresh(self):
        Update_Cache().main()
        self.load_cache()
        self.show('essential', show_alerts=True)

    def show_weather_alerts(self):
        self.load_cache()

        if len(self.weather_alerts) == 0:
            print('No weather alerts.')
            return

        [print(alert) for alert in self.weather_alerts]

    def beachcam(self):
        cmd = f'{self.browser} --new-tab --url {self.beachcam_url}'
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        exit()

    def ipma(self):
        url = '"https://www.ipma.pt/en/otempo/prev.localidade.hora/#'
        cmd = f'{self.browser} --new-tab --url {url}{self.ipma_place}'
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        exit()


class Update_Cache:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.weather_cache_path = self.config['GENERAL']['cache_path']
        local_lat = self.config['GENERAL']['local_latitude']
        local_lon = self.config['GENERAL']['local_longitude']
        api_key = self.config['GENERAL']['api_key']

        self.current_weather_url = 'https://api.weatherbit.io/v2.0/current?' \
            f'lat={local_lat}&lon={local_lon}&key={api_key}&include=alerts'
        self.forecast_weather_url = 'https://api.weatherbit.io/v2.0/forecast' \
            f'/daily?lat={local_lat}&lon={local_lon}&key={api_key}'

    def main(self):
        self.get_info()
        self.select_info()
        self.update_cache_file()

    def get_info(self):
        current_weather_data = requests.get(self.current_weather_url).text
        self.current_weather_data = json.loads(current_weather_data)['data'][0]
        self.weather_alerts = json.loads(current_weather_data)['alerts']
        forecast_weather_data = requests.get(self.forecast_weather_url).text
        self.forecast_weather_data = json.loads(forecast_weather_data)['data']

    def select_info(self):
        self.current_weather_info, self.forecast_weather_info = {}, []

        self.current_weather_info['last_update'] = \
            self.current_weather_data['ob_time']
        self.current_weather_info['location'] = \
            self.current_weather_data['city_name']
        self.current_weather_info['curr_temp'] = \
            self.current_weather_data['temp']
        self.current_weather_info['curr_ftemp'] = \
            self.current_weather_data['app_temp']

        for day in self.forecast_weather_data:
            entry = {}
            entry['date'] = day['valid_date']
            date = datetime.strptime(day['valid_date'], '%Y-%m-%d')
            entry['week_day'] = datetime.strftime(date, '%A')
            entry['weather'] = day['weather']['description']
            entry['max_temp'] = day['max_temp']
            entry['min_temp'] = day['min_temp']
            entry['rain_prob'] = day['pop']
            entry['rain_size'] = round(day['precip'], 2)
            entry['wind_spd'] = day['wind_spd']
            entry['hmd_prctg'] = day['rh']
            entry['cld_prctg'] = day['clouds']
            entry['uv_index'] = day['uv']
            sunrise = day['sunrise_ts']
            entry['sunrise'] = datetime.fromtimestamp(
                sunrise).strftime('%H:%M:%S')
            sunset = day['sunset_ts']
            entry['sunset'] = datetime.fromtimestamp(
                sunset).strftime('%H:%M:%S')
            self.forecast_weather_info.append(entry)

    def update_cache_file(self):
        with open(self.weather_cache_path, 'wb') as wc:
            pickle.dump([self.current_weather_info,
                         self.forecast_weather_info,
                         self.weather_alerts], wc)


if len(sys.argv) > 1:
    if sys.argv[1] == 'update_cache':
        Update_Cache().main()
    else:
        print('Argument error...')
else:
    we = Weather()
    title = 'Weather-Menu'
    keys = {'ls': (lambda: we.show('essential'), 'show weather info'),
            'la': (lambda: we.show('all'), 'show all weather info'),
            'r': (we.refresh, 'refresh all weather info'),
            'a': (we.show_weather_alerts, 'show weather alerts'),
            'c': (we.beachcam, 'open beachcam on the browser'),
            'i': (we.ipma, 'open ipma on the browser')}
    extra_func = (lambda: we.show('essential', show_alerts=True))
    gmenu(title, keys, extra_func)
