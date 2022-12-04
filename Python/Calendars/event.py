#!/usr/bin/python3

from Tfuncs import rofi

import subprocess
from datetime import datetime, timedelta

from utils import Utils


class Event:
    def __init__(self) -> None:
        self.utils = Utils()

    @staticmethod
    def show(calendar: str, weeks: str) -> None:
        try:
            if int(weeks) < 1:
                print("Invalid number of weeks...")
                return
        except ValueError:
            print("Weeks must be a number...")
            return

        today = datetime.now().strftime("%d/%m/%Y")
        today_strp = datetime.strptime(today, "%d/%m/%Y")

        end_date_strp = today_strp + timedelta(days=int(weeks) * 7)
        end_date = end_date_strp.strftime("%d/%m/%Y")

        cmd = (
            f"khal list {today} {end_date}"
            if calendar == "all"
            else f"khal list -a {calendar} {today} {end_date}"
        )
        subprocess.run(cmd, shell=True)

    def add_personal(
        self, title: str | None = None, use_rofi: bool = False
    ) -> None:
        title = self.utils.get_title(
            event="personal", title=title, use_rofi=use_rofi
        )
        if title == "q":
            print("Aborting...")
            return

        date = self.utils.get_date(event="personal", use_rofi=use_rofi)
        if date == "q":
            print("Aborting...")
            return

        hour = self.utils.get_hour("beginning", use_rofi=use_rofi)
        if hour == "q":
            print("Aborting...")
            return

        alarm_msg = (
            "[1] at the beginning of the event\n[2] 3h "
            "before\n[3] 6h before\n[4] 1 day before\n"
            "[5] 3 days before\n[6] 7 days before\n[7] 14 days "
            "before\n[8] 21 days"
        )
        alarm_qst = "Enter the alarms (e.g.: 2+5+1), " "or leave empty for none"
        alarm_opts = {
            "1": "0m",
            "2": "3h",
            "3": "6h",
            "4": "1d",
            "5": "3d",
            "6": "7d",
            "7": "14d",
            "8": "21d",
        }
        print(alarm_msg)
        message = alarm_msg
        while True:
            if use_rofi:
                alarm = rofi.simple_prompt(alarm_qst, message)
            else:
                alarm = input(alarm_qst + ": ")
            if alarm == "q":
                print("Aborted...")
                return
            elif alarm == "":
                break

            if alarm in alarm_opts.keys():
                alarm = "--alarms " + alarm_opts[alarm]
                break
            else:
                if "+" in alarm:
                    alarms_list = alarm.split("+")
                    alarm = "--alarms " + ",".join(
                        [alarm_opts[alarm] for alarm in alarms_list]
                    )
                    break
                message = "Invalid answer..."
                print(message)

        description, category, special_options = "", "", False
        question = "Do you want any special option (Description or end-hour)?"
        if use_rofi:
            dmenu = ["No", "Yes"]
            ans = rofi.custom_dmenu(question, dmenu)
            if ans == "Yes":
                special_options = True
        else:
            if input(f":: {question} [y/N] ") == "y":
                special_options = True

        if special_options:
            question = (
                "Enter the description for the event, "
                "or leave empty for none"
            )
            if use_rofi:
                description = rofi.simple_prompt(question)
            else:
                description = input(question + ": ")
            if description == "q":
                print("Aborted...")
                return
            description = (
                ':: "' + description + '"' if description != "" else ""
            )

            if hour != "":
                # Muda a variável pq a função self.get_hour dá self.hour
                hour_ending = self.utils.get_hour("ending", use_rofi=use_rofi)
                if hour_ending == "q":
                    print("Aborted...")
                    return
                elif hour_ending != "":
                    hour += "-" + hour_ending

        cmd = (
            f'khal new -a personal {date} {hour} "{title}" '
            f"{description} {category} {alarm}"
        )
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            msg = "Error adding the calendar event..."
        else:
            msg = "Calendar event added successfuly!"

        if use_rofi:
            rofi.message(msg)
        else:
            print(msg)

    def add_recurrent(self) -> None:
        title = self.utils.get_title(event="recurrent")
        if title == "q":
            print("Aborting...")
            return

        date = self.utils.get_date(event="recurrent")
        if date == "q":
            print("Aborting...")
            return

        recurrence_opts = {
            "1": "-r yearly",
            "2": "-r monthly",
            "3": "-r weekly",
            "4": "-r daily",
        }
        recurrence = input(
            "[1]: yearly\n[2]: monthly\n[3]: weekly\n[4]: "
            "daily\nEnter the recurrence: "
        )
        if recurrence not in recurrence_opts.keys():
            print("Aborted...")
            return
        recurrence = recurrence_opts[recurrence]

        cmd = (
            f'khal new -a recurrent {date} "{title}"'
            f" {recurrence} --alarms -12h"
        )
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print("Error adding the calendar event...")
            return
        print("Calendar event added successfuly!")
        print(f"Alarm at 12:00 on {date}")

    def add_birthday(self) -> None:
        title = self.utils.get_title(event="birthday")
        if title == "q":
            print("Aborting...")
            return

        date = self.utils.get_date(event="recurrent")
        if date == "q":
            print("Aborting...")
            return

        description = input(
            "Enter a description for this person, or leave empty for none: "
        )
        if description == "q":
            print("Aborting...")
            return
        description = ':: "' + description + '"' if description != "" else ""

        cmd = (
            f'khal new -a birthdays {date} "{title}" '
            f"{description} -r yearly --alarms -12h"
        )
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print("Error adding the calendar event...")
            return
        print("Calendar event added successfuly!")
        print(f"Alarm at 12:00 on {date}")

    @staticmethod
    def edit(calendar: str) -> None:
        if calendar == "birthdays":
            question = (
                "Enter the name or aproximate name of the person "
                " to edit, or <q> to quit: "
            )
        else:
            question = (
                "Enter the title or aproximate title of the event "
                "to edit, or <q> to quit: "
            )

        title = input(question)
        if title == "q":
            print(
                "Aborting...\nTry the 'ls' option to have an ideia of the event title"
            )
            return

        subprocess.run(["khal", "edit", "-a", calendar, title])
