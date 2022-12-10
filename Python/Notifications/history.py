#!/usr/bin/python3
# The Updater should be triggered after each notification, or as a daemon

from Tfuncs import fcol, ffmt

from datetime import datetime, timedelta

from utils import Utils


class History:
    def __init__(self) -> None:
        self.utils = Utils()
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d %H:%M")
        self.notifs_history = self.utils.History().get_notifs_history()

    @staticmethod
    def update_hist() -> None:
        Updater().main()

    def show_new_notifs(self) -> None:
        if not self.utils.History().check_for_new_notifs():
            print("No new notifications...")
            return

        new_notifs = self.utils.History().get_new_notifs()
        self.utils.History().remove_new_notifs()

        print(f"{ffmt.bold}{fcol.red}NEW:{ffmt.reset}")
        print(
            *(f'{notif["time"]} - {notif["message"]}' for notif in new_notifs),
            sep="\n",
        )

    def show_all(self) -> None:
        for day in sorted(self.notifs_history):
            if day[0] == self.now.split()[0]:
                print(ffmt.bold + fcol.green + "\nTODAY:" + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + "\n" + day[0] + ":" + ffmt.reset)
            print(
                *(f'{notif["time"]} - {notif["message"]}' for notif in day[1]),
                sep="\n",
            )

    def show_all_filter_urg(self, urg_level: str) -> None:
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

        for day in sorted(self.notifs_history):
            if day[0] == self.now.split()[0]:
                print(ffmt.bold + fcol.green + "\nTODAY:" + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + "\n" + day[0] + ":" + ffmt.reset)
            notifs = [
                f'{notif["time"]} - {notif["message"]}'
                for notif in day[1]
                if notif["urgency"] == urg_level
            ]
            if len(notifs) == 0:
                print("None")
            else:
                print("\n".join(notifs))


class Updater:
    def __init__(self) -> None:
        self.utils = Utils()
        self.now = datetime.now()
        self.today = self.now.strftime("%Y-%m-%d")

    def main(self) -> None:
        dunst_hist = self.utils.History().get_dunst_hist()
        if len(dunst_hist) == 0:
            return

        self.get_last_entries_id()
        if self.check_dunst_last() is False:
            return
        if self.check_if_new() is False:
            return
        self.get_new_list()
        self.refresh_lists()

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
