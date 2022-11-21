#!/usr/bin/python3


class Questions:
    @staticmethod
    def get_date(
        question: str,
        date_type: str = "%Y-%m-%d",
        answer: str | None = None,
        use_rofi: bool = False,
    ) -> str:
        from Tfuncs import rofi

        from datetime import datetime

        message = ""
        while True:
            if answer is None:
                date = (
                    rofi.simple_prompt(question, message)
                    if use_rofi
                    else input(question)
                )
            else:
                date = answer

            if date == "q":
                return date

            current_year = datetime.now().strftime("%Y")
            if date == "":
                date = datetime.now().strftime("%d-%m-%Y")
            elif date.count("-") == 0:
                current_month = datetime.now().strftime("%m")
                date = date + "-" + current_month + "-" + current_year
            elif date.count("-") == 1:
                date = date + "-" + current_year

            date_d, date_m, date_y = date.split("-")
            if len(date_m) == 1:
                date_m = "0" + date_m
            if len(date_y) == 2:
                date_y = "20" + date_y
            date = date_d + "/" + date_m + "/" + date_y
            try:
                date = datetime.strptime(date, "%d/%m/%Y")
                return date.strftime(date_type)
            except ValueError:
                message = "Invalid date"
                print(message)
                if answer is not None:
                    return "q"

    @staticmethod
    def get_hour(
        question: str,
        hour_type: str = "%H:%M:%S",
        answer: str | None = None,
        use_rofi: bool = False,
    ) -> str:
        from Tfuncs import rofi

        from datetime import datetime

        message = ""
        while True:
            if answer is None:
                hour = (
                    rofi.simple_prompt(question, message)
                    if use_rofi
                    else input(question)
                )
            else:
                hour = answer

            if hour == "q":
                return hour
            elif hour == "":
                hour = "09-00"
            elif hour.count("-") == 0:
                hour = hour + "-" + "00"
            hour = hour.replace("-", ":")
            try:
                hour = datetime.strptime(hour, hour_type)
            except ValueError:
                message = "Invalid hour"
                print(message)
                if answer is not None:
                    return "q"
                continue
            break
        return hour.strftime(hour_type)
