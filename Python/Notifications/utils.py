import re
import os
import subprocess
import pickle
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, Generator

from notifs import Notif, ScheduledNotif, Urgency


class Utils:
    hist_path = "history_path"
    unseen_notif_path = "unseen_notif_path"
    scheduled_path = "scheduled_path"

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
            cmd.append(f"--urgency={urgency}")
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

    def get_scheduled_notifs(self) -> list[ScheduledNotif]:
        if self.check_for_file(self.scheduled_path):
            return self.load_pkl(self.scheduled_path)
        return list()

    def save_scheduled_notifs(self, notifs: list[ScheduledNotif]) -> None:
        self.write_pkl(self.scheduled_path, notifs)

    def get_unseen_notifs(self) -> list[Notif]:
        if self.check_for_file(self.unseen_notif_path):
            return self.load_pkl(self.unseen_notif_path)
        return list()

    def save_unseen_notifs(self, notifs: list[Notif]) -> None:
        self.write_pkl(self.unseen_notif_path, notifs)

    def remove_unseen_notifs(self) -> None:
        os.remove(self.unseen_notif_path)

    def get_today_notifs_history(self) -> tuple[list[Notif], str]:
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.hist_path, today)
        if self.check_for_file(file_path):
            return self.load_pkl(file_path), file_path
        return list(), file_path

    def save_today_notifs_history(
        self, notifs: list[Notif], history_file_path: str
    ) -> None:
        self.write_pkl(history_file_path, notifs)

    def get_notifs_history(self) -> list[list[Notif]]:
        hist_files = self.get_history_files()
        return [self.load_pkl(file) for file in hist_files]

    def get_history_files(self) -> list[str]:
        return [
            os.path.join(self.hist_path, file)
            for file in os.listdir(self.hist_path)
        ]

    def check_for_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            return True
        return False

    def write_pkl(
        self, file_path: str, notifs: list[Notif | ScheduledNotif]
    ) -> None:
        with open(file_path, "wb") as f:
            pickle.dump(notifs, f)

    def load_pkl(self, file_path: str) -> list[Notif | ScheduledNotif]:
        with open(file_path, "rb") as f:
            return pickle.load(f)


class Date:
    def prompt_date(self, *args) -> Optional[str]:
        pass

    def prompt_hour(self, *args) -> Optional[str]:
        pass

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
