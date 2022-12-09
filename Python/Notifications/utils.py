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
            with open(self.scheduled_path, "wb") as sn:
                pickle.dump([cal_notifs_last_update, notifs], sn)

        def load_file(self) -> tuple[str, list]:
            with open(self.scheduled_path, "rb") as sn:
                return pickle.load(sn)

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

        # reduzir!
        def get_dunst_hist(self):
            self.notif_hist_path = os.path.join(
                self.hist_path, f"{self.today_date}.pkl"
            )
            self.dunst_hist_path = "/tmp/dunst_history.json"

            """foi feito assim pra ficar imediatamente em formato json;
            doutra forma teria que se recorrer a regex, ou algo do género"""
            subprocess.run(
                f"dunstctl history > {self.dunst_hist_path}", shell=True
            )
            with open(self.dunst_hist_path, "r") as dh:
                dunst_hist_dict = json.load(dh)

            self.dunst_hist_list = dunst_hist_dict["data"][0]
            os.remove(self.dunst_hist_path)

            if os.path.exists(self.notif_hist_path):
                with open(self.notif_hist_path, "rb") as nh:
                    self.notif_hist_list = pickle.load(nh)
                self.check_yesterday = False
            else:
                self.notif_hist_list = []
                self.check_yesterday = False
                self.yesterday = str(
                    (self.now - timedelta(days=1)).strftime("%Y-%m-%d")
                )
                self.notif_yhist_path = os.path.join(
                    self.hist_path, f"{self.yesterday}.pkl"
                )
                if os.path.exists(self.notif_yhist_path):
                    self.check_yesterday = True

        def write_file(self, file: str, notifs: list[dict]) -> None:
            with open(file, "wb") as sn:
                pickle.dump(notifs, sn)

        def load_file(self, file: str) -> list[dict]:
            with open(file, "rb") as sn:
                return pickle.load(sn)
