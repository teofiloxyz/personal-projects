#!/usr/bin/python3

import os
import subprocess
import pickle


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
            with open(self.scheduled_path, "wb") as sn:
                pickle.dump([cal_notifs_last_update, notifs], sn)

        def load_file(self) -> tuple[str, list]:
            with open(self.scheduled_path, "rb") as sn:
                return pickle.load(sn)

    class History:
        def get_notif_list(pkl_path):
            with open(pkl_path, "rb") as pkl:
                notif_list = pickle.load(pkl)
                notif_list.reverse()
                return notif_list
