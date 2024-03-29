from Tfuncs import Rofi

import re
import os
import subprocess
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, Generator

from notifs import Urgency


class Utils:
    def send_notification(
        self,
        title: str,
        message: str,
        urgency: Urgency,
        category: str = "",
        muted: bool = False,
    ) -> None:
        if not muted:
            self.play_sound()
        cmd = ["notify-send", title, message]
        if urgency != "":
            cmd.append(f"--urgency={urgency.value}")
        if category != "":
            cmd.append(f"--category={category}")
        subprocess.Popen(cmd)

    def play_sound(self) -> None:
        notif_sound = "notif_sound.wav"
        subprocess.Popen(["paplay", notif_sound])

    def shell_generator(self, cmd: str) -> Generator:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        while True:
            yield process.stdout.readline().decode("utf-8").rstrip()

    def extract_substr_from_str(
        self, regex: str, string: str, not_found_str: str = ""
    ) -> str:
        substr = re.search(regex, string)
        if substr:
            return substr.group(1)
        return not_found_str


class Date:  # improve prompt funcs
    rofi = Rofi()

    def prompt_date(
        self,
        question: str,
        date_type: str = "%Y-%m-%d",
        answer: Optional[str] = None,
        use_rofi: bool = False,
    ) -> Optional[str]:
        message = ""
        while True:
            if answer is None:
                date = (
                    self.rofi.simple_prompt(question, message)
                    if use_rofi
                    else input(question)
                )
            else:
                date = answer

            if date == "q":
                return None

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
                if answer:
                    return None

    def prompt_hour(
        self,
        question: str,
        hour_type: str = "%H:%M:%S",
        answer: Optional[str] = None,
        use_rofi: bool = False,
    ) -> Optional[str]:
        message = ""
        while True:
            if answer is None:
                hour = (
                    self.rofi.simple_prompt(question, message)
                    if use_rofi
                    else input(question)
                )
            else:
                hour = answer

            if hour == "q":
                return None
            elif hour == "":
                hour = "09-00-00"
            elif hour.count("-") == 0:
                hour = hour + 2 * ("-" + "00")
            elif hour.count("-") == 1:
                hour = hour + ("-" + "00")
            hour = hour.replace("-", ":")
            try:
                hour = datetime.strptime(hour, hour_type)
            except ValueError:
                message = "Invalid hour"
                print(message)
                if answer:
                    return None
                continue
            break
        return hour.strftime(hour_type)

    def get_date_now(self, date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(date_format)

    def get_date_strp(
        self, date_string: str, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        return datetime.strptime(date_string, date_format)

    def get_date_strf(
        self, date: datetime, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        return datetime.strftime(date, date_format)

    def get_date_limit_strp(
        self, days: int = 30, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        now = self.get_date_now(date_format=date_format)
        now_strp = self.get_date_strp(now, date_format)
        return now_strp + timedelta(days=days)

    def get_date_from_unix_time(self, unix_time: float) -> str:
        return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

    def get_file_modif_date(self, file_path: str) -> str:
        file_modif_unix_time = os.path.getmtime(file_path)
        return self.get_date_from_unix_time(file_modif_unix_time)

    def check_if_date_a_is_newer(
        self,
        date_a: datetime,
        date_b: datetime,
    ) -> bool:
        if date_a > date_b:
            return True
        return False

    def check_if_date_is_due(self, date_strp: datetime) -> bool:
        now = self.get_date_now()
        now_strp = self.get_date_strp(now)
        if now_strp >= date_strp:
            return True
        return False

    def get_date_with_delay(
        self,
        date_strp: datetime,
        delay_from_date_secs: int,
        delay_is_negative: bool,
    ) -> datetime:
        if delay_is_negative:
            return date_strp - timedelta(seconds=delay_from_date_secs)
        return date_strp + timedelta(seconds=delay_from_date_secs)

    def correct_recurrent_calendar_date(
        self, notif_date_strp: datetime, event_recurrency: str
    ) -> datetime:
        now = self.get_date_now()
        now_strp = self.get_date_strp(now)
        while now_strp >= notif_date_strp:
            if event_recurrency == "YEARLY":
                notif_date_strp += relativedelta(years=1)
            elif event_recurrency == "MONTHLY":
                notif_date_strp += relativedelta(months=1)
            elif event_recurrency == "WEEKLY":
                notif_date_strp += relativedelta(days=7)
        return notif_date_strp
