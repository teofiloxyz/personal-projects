#!/usr/bin/python3

import subprocess

from utils import Utils


class Browser:
    def __init__(self) -> None:
        self.utils = Utils()
        self.browser = "browser"

        # Add whatever you want
        self.options = {
            "s": "",
            "p": "python ",
            "b": "bash ",
            "g": "golang ",
            "la": "latex ",
            "l": "linux ",
        }

    def main(self, cmd_arg: str) -> None:
        option, entry = self.utils.divide_arg(cmd_arg, self.options)
        search_url = self.get_search_url(option, entry)
        self.search_on_browser(search_url)

    def get_search_url(self, option: str, entry: str) -> str:
        search_url = option + entry
        return search_url.replace(" ", "+")

    def search_on_browser(self, search_url) -> None:
        cmd = f"{self.browser} --new-tab --url google.com/{search_url}"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
