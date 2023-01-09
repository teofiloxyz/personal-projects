#!/usr/bin/python3
# The Updater should be triggered after each notification, or as a daemon
# Not tested... still needs a lot of work

from Tfuncs import fcol, ffmt

from datetime import datetime, timedelta
import re

from utils import Utils


class History:
    def __init__(self) -> None:
        self.utils = Utils().History()
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d %H:%M")
        self.notifs_history = self.utils.get_notifs_history()

    @staticmethod
    def update_hist() -> None:
        Updater().main()

    def show_unseen_notifs(self) -> None:
        if not self.utils.check_for_unseen_notifs():
            print("No new notifications...")
            return

        unseen_notifs = self.utils.get_unseen_notifs()
        self.utils.remove_unseen_notifs()

        print(f"{ffmt.bold}{fcol.red}NEW:{ffmt.reset}")
        print(
            *(
                f'{notif["time"]} - {notif["message"]}'
                for notif in unseen_notifs
            ),
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


# Big mess...
class Updater:
    def __init__(self) -> None:
        self.utils = Utils()
        self.now = datetime.now()
        self.today = self.now.strftime("%Y-%m-%d")

    def main(self) -> None:
        notifs, sender = dict(), "0"
        cmd = "dbus-monitor interface='org.freedesktop.Notifications'"
        for line in self.utils.shell_generator(cmd):
            line = " ".join(line.split())
            if line.startswith("method call time="):
                item = re.search("sender=:(.+) ->", line)
                if item:
                    sender = item.group(1)
                    notifs[sender] = dict()
                item = re.search("time=(.[0-9]+)\.", line)
                if item:
                    time = item.group(1)
                    notifs[sender]["time"] = time
                    notifs[sender]["body"] = list()
            elif line.startswith("signal time="):
                item = re.search("destination=:(.+) serial=", line)
                if item:
                    destination = item.group(1)
                    if destination in notifs.keys():
                        time = notifs[destination]["time"]
                        body = notifs[destination]["body"]
                        title = body[3].strip("string ")
                        message = body[4].strip("string ")
                        index = body.index('string "urgency"')
                        urgency = body[index + 1][-1]
                        urgs = ["low", "normal", "critical"]
                        urgency = urgs[int(urgency)]
                        category = ""
                        if 'string "category"' in body:
                            index = body.index('string "category"')
                            category = body[index + 1]
                            category = category.strip("variant string ")
                        del notifs[destination]
                        sender = "0"
                        self.update_notifs_lists(
                            time, title, message, urgency, category
                        )
            else:
                if sender == "0":
                    notifs[sender] = dict()
                    notifs[sender]["body"] = list()
                notifs[sender]["body"].append(line)

    def get_notif_time(self, notif: dict) -> str:
        notif_time = notif["timestamp"]["data"]
        with open("/proc/uptime", "r") as ut:
            os_uptime_in_secs = float(ut.readline().split()[0])

        time_diff_in_secs = os_uptime_in_secs - float(notif_time) / 1000000
        return (self.now - timedelta(seconds=time_diff_in_secs)).strftime(
            "%H:%M:%S"
        )

    def update_notifs_lists(
        self, date: str, title: str, message: str, urgency: str, category: str
    ) -> None:
        entry = {
            "date": date,
            "title": title,
            "message": message,
            "urgency": urgency,
            "category": category,
        }
        # needs fixing
        notifs_hist.append(entry)
        unseen_notifs.append(entry)
