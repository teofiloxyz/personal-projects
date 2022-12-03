#!/usr/bin/python3

from Tfuncs import rofi, qst


class Utils:
    @staticmethod
    def get_title(
        event: str, title: str | None = None, use_rofi: bool = False
    ) -> str:
        message = ""
        while True:
            if title is None:
                question = (
                    "Who's the lucky person to have its birthday noted"
                    if event == "birthday"
                    else "Enter the descriptive title for the event"
                )
                if use_rofi:
                    title = rofi.simple_prompt(question, message)
                else:
                    title = input(question + ": ")

            if 0 < len(title) <= 30:
                break
            else:
                message = "Title is too large, try another..."
                print(message)

        if event == "birthday":
            title = "Aniversário: " + title
        return title

    @staticmethod
    def get_date(event: str, use_rofi: bool = False) -> str:
        if event == "birthday":
            question = (
                "Enter the date for the birthday (e.g.: 20-2; 3 = 3-"
                "curr.month): "
            )
        else:
            question = (
                "Enter the date for the event (e.g.: 28-8-21; 28 = "
                "28-curr.M-curr.Y): "
            )

        return qst.get_date(question, date_type="%d/%m/%Y", use_rofi=use_rofi)

    @staticmethod
    def get_hour(time: str, use_rofi: bool = False) -> str:
        if time == "beginning":
            question = (
                "Enter the hour of the event (e.g.: 9-35; "
                "9 = 9-00) or leave empty for all day: "
            )
        else:
            question = (
                "Enter the hour for the end of the event (e.g.: "
                "18-23; 18 = 18-00) or leave empty for none: "
            )

        return qst.get_hour(question, hour_type="%H:%M", use_rofi=use_rofi)
