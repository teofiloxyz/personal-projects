#!/usr/bin/python3

from Tfuncs import gmenu

import argparse

from weather import Weather
from api import API


def main() -> None:
    update = cmd()
    if update is not None:
        API().update_cache()
    else:
        open_menu()


def cmd() -> tuple:
    args = parser.parse_args()
    return args.update


def open_menu() -> None:
    we = Weather()
    title = "Weather-Menu"
    keys = {
        "ls": (lambda: we.show("essential"), "show weather info"),
        "la": (lambda: we.show("all"), "show all weather info"),
        "r": (we.refresh, "refresh all weather info"),
        "a": (we.show_weather_alerts, "show weather alerts"),
        "c": (we.beachcam, "open beachcam on the browser"),
        "i": (we.ipma, "open ipma on the browser"),
    }
    extra_func = lambda: we.show("essential", show_alerts=True)
    gmenu(title, keys, extra_func)


if __name__ == "__main__":
    main()
