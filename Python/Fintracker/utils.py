#!/usr/bin/python3

import json
from datetime import datetime, timedelta


class Utils:
    def write_json(self, json_info: dict) -> None:
        with open("config.json", "w") as cf:
            json.dump(json_info, cf)

    def load_json(self) -> dict:
        with open("config.json", "r") as cf:
            return json.load(cf)

    def get_date_now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_date_today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def get_date_limit(self, days: int = 30) -> str:
        now = datetime.now().strftime("%Y-%m-%d")
        now_strp = datetime.strptime(now, "%Y-%m-%d")
        return datetime.strftime(now_strp - timedelta(days=days), "%Y-%m-%d")
