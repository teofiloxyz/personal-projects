#!/usr/bin/python3

import json
from datetime import datetime, timedelta


class Utils:
    def get_date_now(self, get_HMS: bool = True) -> str:
        date_format = "%Y-%m-%d %H:%M:%S" if get_HMS else "%Y-%m-%d"
        return datetime.now().strftime(date_format)

    def get_date_strp(self, date_string: str, date_format: str) -> datetime:
        return datetime.strptime(date_string, date_format)

    def get_date_limit(self, days: int = 30) -> str:
        now = self.get_date_now(get_HMS=False)
        now_strp = self.get_date_strp(now, "%Y-%m-%d")
        return datetime.strftime(now_strp - timedelta(days=days), "%Y-%m-%d")

    @staticmethod
    def write_json(json_info: dict) -> None:
        with open("config.json", "w") as cf:
            json.dump(json_info, cf)

    @staticmethod
    def load_json() -> dict:
        with open("config.json", "r") as cf:
            return json.load(cf)

    @staticmethod
    def get_val_as_currency(amount: int) -> str:
        if amount >= 0:
            return "€ {:,.2f}".format(amount)
        else:
            return "(€ {:,.2f})".format(-amount)
