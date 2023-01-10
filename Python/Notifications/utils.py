import os
import subprocess
import pickle
import re
from typing import Generator
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notif:
    date: str
    title: str
    message: str
    urgency: str
    category: str


class Utils:
    def send_notification(
        self, message: str, submessage: str = "", muted: bool = False
    ) -> None:
        if not muted:
            self.play_sound()
        subprocess.Popen(["notify-send", message, submessage])

    def play_sound(self) -> None:
        notif_sound = "notif_sound.wav"
        subprocess.Popen(["paplay", notif_sound])

    def shell_generator(self, cmd: str) -> Generator:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        while True:
            yield process.stdout.readline().decode("utf-8").rstrip()

    def extract_str_from_substr(
        self, regex: str, string: str, not_found_str: str = ""
    ) -> str:
        substr = re.search(regex, string)
        if substr:
            return substr.group(1)
        return not_found_str

    def get_date_from_unix_time(self, unix_time: float) -> str:
        return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

    class Scheduled:
        def __init__(self) -> None:
            self.scheduled_path = "scheduled_path"
            self.check_file()

        def check_file(self) -> None:
            if not os.path.exists(self.scheduled_path):
                self.write_file("2000-01-01 00:00:00", [])

        def write_file(
            self, cal_notifs_last_update: str, notifs: list[dict]
        ) -> None:
            with open(self.scheduled_path, "wb") as f:
                pickle.dump([cal_notifs_last_update, notifs], f)

        def load_file(self) -> tuple[str, list]:
            with open(self.scheduled_path, "rb") as f:
                return pickle.load(f)

    class History:
        hist_path = "history_path"
        unseen_notif_path = "unseen_notif_path"

        def check_for_notifs_file(self, file_path: str) -> bool:
            if os.path.exists(file_path):
                return True
            return False

        def get_unseen_notifs(self) -> list[Notif]:
            if self.check_for_notifs_file(self.unseen_notif_path):
                return self.load_pkl(self.unseen_notif_path)
            return list()

        def save_unseen_notifs(self, notifs: list[Notif]) -> None:
            self.write_pkl(self.unseen_notif_path, notifs)

        def remove_unseen_notifs(self) -> None:
            os.remove(self.unseen_notif_path)

        def get_today_notifs_history(self) -> tuple[list[Notif], str]:
            today = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join(self.hist_path, today)
            if self.check_for_notifs_file(file_path):
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

        def write_pkl(self, file_path: str, notifs: list[Notif]) -> None:
            with open(file_path, "wb") as f:
                pickle.dump(notifs, f)

        def load_pkl(self, file_path: str) -> list[Notif]:
            with open(file_path, "rb") as f:
                return pickle.load(f)
