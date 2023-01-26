#!/usr/bin/python3

from Tfuncs import Menu

import argparse

from weather import Weather
from api import API


def handle_cmd_args() -> tuple:
    parser = argparse.ArgumentParser(description="Weather")
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="updates cache",
    )
    args = parser.parse_args()
    return args.update


def open_menu() -> None:
    weather = Weather()
    menu = Menu(
        title="Weather-Menu", beginning_func=lambda: weather.show("essential")
    )

    menu.add_option(
        key="ls",
        func=lambda: weather.show("essential"),
        help="show weather info",
    )
    menu.add_option(
        key="la", func=lambda: weather.show("all"), help="show all weather info"
    )
    menu.add_option(
        key="r", func=weather.refresh, help="refresh all weather info"
    )
    menu.add_option(
        key="a", func=weather.show_weather_alerts, help="show weather alerts"
    )
    menu.add_option(key="i", func=weather.ipma, help="open ipma on the browser")
    menu.add_option(
        key="c", func=weather.beachcam, help="open beachcam on the browser"
    )

    menu.start()


def main() -> None:
    update = handle_cmd_args()
    if update:
        API().update_cache()
    else:
        open_menu()


if __name__ == "__main__":
    main()
