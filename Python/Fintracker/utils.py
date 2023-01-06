import json
from datetime import datetime, timedelta
from dataclasses import dataclass


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
    def get_val_as_currency(amount: float) -> str:
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

    def save(self) -> None:
        self.write_json("auto_transactions.json", Fintracker.auto_transactions)
        self.write_json("balance.json", Fintracker.balance)


@dataclass
class Fintracker:
    auto_transactions = Utils().load_json("auto_transactions.json")
    balance = Utils().load_json("balance.json")
