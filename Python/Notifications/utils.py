#!/usr/bin/python3

import os
import subprocess
import json
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
            with open(self.scheduled_path, "wb") as f:
                pickle.dump([cal_notifs_last_update, notifs], f)

        def load_file(self) -> tuple[str, list]:
            with open(self.scheduled_path, "rb") as f:
                return pickle.load(f)

    class History:
        def __init__(self) -> None:
            self.hist_path = "history_path"
            self.unseen_notif_path = "unseen_notif_path"

        def check_for_unseen_notifs(self) -> bool:
            if os.path.exists(self.unseen_notif_path):
                return True
            return False

        def get_unseen_notifs(self) -> list[dict[str, str]]:
            return self.get_file_notifs(self.unseen_notif_path)

        def remove_unseen_notifs(self) -> None:
            os.remove(self.unseen_notif_path)

        def get_history_files(self) -> list[str]:
            return [
                os.path.join(self.hist_path, file)
                for file in os.listdir(self.hist_path)
            ]

        def get_file_notifs(self, hist_file: str) -> list[dict[str, str]]:
            with open(hist_file, "rb") as pkl:
                notifs = pickle.load(pkl)
                return notifs.reversed()

        def get_file_date(self, hist_file: str) -> str:
            return hist_file.split(".")[0]

        def get_notifs_history(self) -> list[tuple[str, list[dict[str, str]]]]:
            hist_files = self.get_history_files
            return [
                (self.get_file_date(file), self.get_file_notifs(file))
                for file in hist_files
            ]

        def get_dunst_hist(self) -> dict:
            """Foi feito assim pra ficar imediatamente em formato json;
            doutra forma teria que se recorrer a regex, ou algo do género"""

            dunst_hist_path = "/tmp/dunst_history.json"
            subprocess.run(f"dunstctl history > {dunst_hist_path}", shell=True)

            dunst_hist = self.load_json_file(dunst_hist_path)
            os.remove(dunst_hist_path)
            return dunst_hist["data"][0]

        def load_json_file(self, file: str) -> dict:
            with open(file, "r") as f:
                return json.load(f)

        def write_file(self, file: str, notifs: list[dict]) -> None:
            with open(file, "wb") as f:
                pickle.dump(notifs, f)

        def load_file(self, file: str) -> list[dict]:
            with open(file, "rb") as f:
                return pickle.load(f)
