#!/usr/bin/python3

import sys
import subprocess
from datetime import datetime, timedelta
from Tfuncs import gmenu, qst, rofi


if __name__ == "__main__":
    if len(sys.argv) > 2:
        title = " ".join(sys.argv[2:])
        if sys.argv[1] == "create_personal_event":
            Calendars().personal_event(title, use_rofi=True)
        else:
            print("Argument error...")
    else:
        cal = Calendars()
        title = "Calendars-Menu"
        keys = {
            "ls": (
                lambda weeks="2", calendar="all": cal.show_events(
                    calendar, weeks
                ),
                "show ALL events for the next two weeks",
                "<# of weeks>: show ALL events for the next # weeks",
            ),
            "lsp": (
                lambda weeks="2", calendar="personal": cal.show_events(
                    calendar, weeks
                ),
                "show personal events for the next two weeks",
                "<# of weeks>: show personal events for the " "next # weeks",
            ),
            "lsr": (
                lambda weeks="2", calendar="recurrent": cal.show_events(
                    calendar, weeks
                ),
                "show recurrent events for the next two weeks",
                "<# of weeks>: show recurrent events for the " "next weeks",
            ),
            "lsb": (
                lambda: cal.show_events(calendar="birthdays", weeks="53"),
                "show all birthdays throughout the year",
            ),
            "ad": (cal.personal_event, "add new event to 'personal'"),
            "adr": (cal.recurrent_event, "add new event to 'recurrent'"),
            "adb": (cal.birthday_event, "add new event to 'birthdays'"),
            "ed": (
                lambda: cal.edit_event(calendar="personal"),
                "edit/remove event from 'personal'",
            ),
            "edr": (
                lambda: cal.edit_event(calendar="recurrent"),
                "edit/remove event from 'recurrent'",
            ),
            "edb": (
                lambda: cal.edit_event(calendar="birthdays"),
                "edit/remove event from 'birthdays'",
            ),
        }
        gmenu(title, keys)
