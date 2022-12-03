#!/usr/bin/python3


class Utils:
    def get_title(self, title=None, use_rofi=False):
        message = ""
        while True:
            if title is None:
                qst = (
                    "Who's the lucky person to have its birthday noted"
                    if self.event == "birthday"
                    else "Enter the descriptive title for the event"
                )
                if use_rofi:
                    self.title = rofi.simple_prompt(qst, message)
                else:
                    self.title = input(qst + ": ")
            else:
                self.title = title
                title = None

            if self.title == "q":
                return False
            elif 0 < len(self.title) <= 30:
                break
            else:
                message = "Title is too large, try another"
                print(message)

        if self.event == "birthday":
            self.title = "Aniversário: " + self.title

    def get_date(self, use_rofi=False):
        if self.event == "birthday":
            question = (
                "Enter the date for the birthday (e.g.: 20-2; 3 = 3-"
                "curr.month): "
            )
        else:
            question = (
                "Enter the date for the event (e.g.: 28-8-21; 28 = "
                "28-curr.M-curr.Y): "
            )

        self.date = qst.get_date(
            question, date_type="%d/%m/%Y", use_rofi=use_rofi
        )
        if self.date == "q":
            return False

    def get_hour(self, time, use_rofi=False):
        if time == "beggining":
            question = (
                "Enter the hour of the event (e.g.: 9-35; "
                "9 = 9-00) or leave empty for all day: "
            )
        else:
            question = (
                "Enter the hour for the end of the event (e.g.: "
                "18-23; 18 = 18-00) or leave empty for none: "
            )

        self.hour = qst.get_hour(question, hour_type="%H:%M", use_rofi=use_rofi)
        if self.hour == "q":
            return False
