import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Date:
    def get_now(self, date_format: str = "%Y-%m-%d") -> str:
        return datetime.now().strftime(date_format)

    def parse(self, date_string: str, date_format: str) -> datetime:
        return datetime.strptime(date_string, date_format)

    def get_limit(self, days: int = 30, date_format: str = "%Y-%m-%d") -> str:
        now = self.get_now(date_format=date_format)
        now_strp = self.parse(now, date_format)
        return datetime.strftime(now_strp - timedelta(days=days), date_format)

    def is_due(self, date_string: str, date_format: str = "%Y-%m-%d") -> bool:
        now = self.get_now(date_format)
        now_strp = self.parse(now, date_format)
        date_strp = self.parse(date_string, date_format)
        if now_strp >= date_strp:
            return True
        return False

    def get_delta(self, recurrence: str) -> timedelta | relativedelta:
        # very simplistic
        if recurrence == "monthly":
            return relativedelta(months=1)
        else:
            return timedelta(days=7)

    def add_delta(
        self,
        date_string: str,
        delta: timedelta | relativedelta,
        date_format: str = "%Y-%m-%d",
    ) -> str:
        date_strp = self.parse(date_string, date_format)
        return datetime.strftime(date_strp + delta, "%Y-%m-%d")


class Utils:
    @staticmethod
    def as_currency(amount: float) -> str:
        if amount >= 0:
            return "€ {:,.2f}".format(amount)
        else:
            return "(€ {:,.2f})".format(-amount)

    @staticmethod
    def write_json(file_path: str, json_info: dict) -> None:
        with open(file_path, "w") as cf:
            json.dump(json_info, cf, indent=4)

    @staticmethod
    def load_json(file_path: str) -> dict:
        with open(file_path, "r") as cf:
            return json.load(cf)
