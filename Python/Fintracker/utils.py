#!/usr/bin/python3


class Utils:
    def save_json(self):
        with open("config.json", "w") as cf:
            json.dump(self.json_info, cf)

    def open_json(self):
        with open("config.json", "r") as cf:
            self.json_info = json.load(cf)
