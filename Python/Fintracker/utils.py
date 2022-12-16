#!/usr/bin/python3

import json


class Utils:
    def write_json(self, json_info: dict) -> None:
        with open("config.json", "w") as cf:
            json.dump(json_info, cf)

    def load_json(self) -> dict:
        with open("config.json", "r") as cf:
            return json.load(cf)
