#!/usr/bin/python3
# Should be triggered after each notification, or as a daemon

import os
import subprocess
import json
import pickle
from datetime import datetime, timedelta


class History:
    def __init__(self):
        self.hist_path = "history_path"
        self.notif_hist_list = [
            (file.split(".")[0], get_notif_list(os.path.join(r_d_f[0], file)))
            for r_d_f in os.walk(self.hist_path)
            for file in r_d_f[2]
        ]
        self.now = datetime.now()
        self.today_date = self.now.strftime("%Y-%m-%d")

    def show_new_notif():
        new_notif_path = "new_path"
        if not os.path.exists(new_notif_path):
            print("No new notifications...")
            return

        print(f"{ffmt.bold}{fcol.red}NEW:{ffmt.reset}")
        notif_list = get_notif_list(new_notif_path)

        print(
            *(f'{notif["time"]} - {notif["message"]}' for notif in notif_list),
            sep="\n",
        )
        os.remove(new_notif_path)

    def show_all(self):
        for day in sorted(self.notif_hist_list):
            if day[0] == self.today_date:
                print(ffmt.bold + fcol.green + "\nTODAY:" + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + "\n" + day[0] + ":" + ffmt.reset)
            print(
                *(f'{notif["time"]} - {notif["message"]}' for notif in day[1]),
                sep="\n",
            )

    def show_filter_urg(self, urg_level):
        col = fcol.bright_white
        if urg_level == "low":
            col = fcol.green
        elif urg_level == "normal":
            col = fcol.yellow
        elif urg_level == "critical":
            col = fcol.red
        print(
            f"Showing all{ffmt.bold}{col} "
            f"{urg_level} urgency {ffmt.reset} past notifications"
        )

        for day in sorted(self.notif_hist_list):
            if day[0] == self.today_date:
                print(ffmt.bold + fcol.green + "\nTODAY:" + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + "\n" + day[0] + ":" + ffmt.reset)
            notif_list = [
                f'{notif["time"]} - {notif["message"]}'
                for notif in day[1]
                if notif["urgency"] == urg_level
            ]
            if len(notif_list) == 0:
                print("None")
            else:
                print("\n".join(notif_list))


class Updater:
    def __init__(self):
        self.hist_path = "history_path"
        self.notif_new_path = "new_path"

    def main(self):
        self.get_date()
        self.get_hist_lists()
        if self.check_dunst_list() is False:
            return
        self.get_last_entries_id()
        if self.check_dunst_last() is False:
            return
        if self.check_if_new() is False:
            return
        self.get_new_list()
        self.refresh_lists()

    def get_date(self):
        self.now = datetime.now()
        self.today_date = self.now.strftime("%Y-%m-%d")

    def get_hist_lists(self):
        self.notif_hist_path = os.path.join(
            self.hist_path, f"{self.today_date}.pkl"
        )
        self.dunst_hist_path = "/tmp/dunst_history.json"

        """foi feito assim pra ficar imediatamente em formato json;
        doutra forma teria que se recorrer a regex, ou algo do género"""
        subprocess.run(f"dunstctl history > {self.dunst_hist_path}", shell=True)
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

    def check_dunst_list(self):
        if len(self.dunst_hist_list) == 0:
            return False

    def get_last_entries_id(self):
        self.dunst_hist_last_id = None

        for notif in self.dunst_hist_list:
            if notif["category"]["data"] != "trash":
                self.dunst_hist_last_id = notif["id"]["data"]
                break

        if len(self.notif_hist_list) != 0:
            self.notif_hist_last_id = self.notif_hist_list[0]["id"]
        else:
            if self.check_yesterday is True:
                with open(self.notif_yhist_path, "rb") as nyh:
                    notif_yhist_list = pickle.load(nyh)
                self.notif_hist_last_id = notif_yhist_list[0]["id"]
            else:
                self.notif_hist_last_id = 0

    def check_dunst_last(self):
        if self.dunst_hist_last_id is None:
            return False

    def check_if_new(self):
        if self.dunst_hist_last_id == self.notif_hist_last_id:
            return False

    def get_new_list(self):
        if os.path.exists(self.notif_new_path):
            with open(self.notif_new_path, "rb") as nn:
                self.notif_new_list = pickle.load(nn)
        else:
            self.notif_new_list = []

    def get_time(self):
        with open("/proc/uptime", "r") as ut:
            uptime_secs = float(ut.readline().split()[0])
        time_secs_diff = uptime_secs - float(self.time) / 1000000
        self.time = str(
            (self.now - timedelta(seconds=time_secs_diff)).strftime("%H:%M:%S")
        )

    def get_urgency(self):
        urgency_opts = {3000000: "low", 10000000: "normal", 0: "critical"}
        try:
            self.urgency = urgency_opts[int(self.urgency)]
        except (ValueError, KeyError):
            self.urgency = "normal"

    def refresh_lists(self):
        n = 0
        for notif in self.dunst_hist_list:
            notif_id = notif["id"]["data"]
            if notif_id == self.notif_hist_last_id:
                break
            if notif["category"]["data"] == "trash":
                continue
            self.time = notif["timestamp"]["data"]
            self.get_time()
            self.urgency = notif["timeout"]["data"]
            self.get_urgency()
            message = notif["summary"]["data"]
            notif_dict = {
                "id": notif_id,
                "time": self.time,
                "urgency": self.urgency,
                "message": message,
            }
            self.notif_hist_list.insert(n, notif_dict)
            self.notif_new_list.insert(n, notif_dict)
            n += 1

        with open(self.notif_hist_path, "wb") as nh:
            pickle.dump(self.notif_hist_list, nh)

        with open(self.notif_new_path, "wb") as nn:
            pickle.dump(self.notif_new_list, nn)


HistoryUpdater().main()
