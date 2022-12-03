#!/usr/bin/python3
# Menu para gerir calendários
# Refactor Event class

from Tfuncs import gmenu

import argparse

from event import Event


def main() -> None:
    title = cmd()
    if title is not None:
        Event().add_personal(" ".join(title), use_rofi=True)
    else:
        open_menu()


def cmd() -> str | None:
    parser = argparse.ArgumentParser(description="Calendars")
    parser.add_argument(
        "-c",
        "--create",
        nargs="*",
        help="directly create a personal event if you provide a title",
    )
    args = parser.parse_args()
    return args.create


def open_menu() -> None:
    event = Event()
    title = "Calendars-Menu"
    keys = {
        "ls": (
            lambda weeks="2", calendar="all": event.show(calendar, weeks),
            "show ALL events for the next two weeks",
            "<# of weeks>: show ALL events for the next # weeks",
        ),
        "lsp": (
            lambda weeks="2", calendar="personal": event.show(calendar, weeks),
            "show personal events for the next two weeks",
            "<# of weeks>: show personal events for the " "next # weeks",
        ),
        "lsr": (
            lambda weeks="2", calendar="recurrent": event.show(calendar, weeks),
            "show recurrent events for the next two weeks",
            "<# of weeks>: show recurrent events for the " "next weeks",
        ),
        "lsb": (
            lambda: event.show(calendar="birthdays", weeks="53"),
            "show all birthdays throughout the year",
        ),
        "ad": (event.add_personal, "add new event to 'personal'"),
        "adr": (event.add_recurrent, "add new event to 'recurrent'"),
        "adb": (event.add_birthday, "add new event to 'birthdays'"),
        "ed": (
            lambda: event.edit(calendar="personal"),
            "edit/remove event from 'personal'",
        ),
        "edr": (
            lambda: event.edit(calendar="recurrent"),
            "edit/remove event from 'recurrent'",
        ),
        "edb": (
            lambda: event.edit(calendar="birthdays"),
            "edit/remove event from 'birthdays'",
        ),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
