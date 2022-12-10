#!/usr/bin/python3
# The Updater should be triggered after each notification, or as a daemon
# Not tested... still needs a lot of work

from Tfuncs import fcol, ffmt

from datetime import datetime, timedelta

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


class Updater:
    def __init__(self) -> None:
        self.utils = Utils().History()
        self.now = datetime.now()
        self.today = self.now.strftime("%Y-%m-%d")

    def main(self) -> None:
        dunst_hist = self.get_dunst_hist()
        if len(dunst_hist) == 0:
            return

        last_notifs_hist_date, last_notifs_hist = self.get_last_notifs_hist()
        last_notifs_hist_is_from_yesterday = self.is_from_yesterday(
            last_notifs_hist_date
        )

        last_dunst_notif_id = self.get_last_dunst_notif_id(dunst_hist)
        if last_dunst_notif_id is None:
            return
        last_hist_notif_id = self.get_last_hist_notif_id(
            last_notifs_hist, last_notifs_hist_is_from_yesterday
        )
        if not self.last_dunst_notif_is_new(
            last_hist_notif_id, last_dunst_notif_id
        ):
            return

        unseen_notifs = self.get_unseen_notifs()

        notifs_hist, unseen_notifs = self.update_notifs_lists(
            dunst_hist, last_notifs_hist, unseen_notifs, last_hist_notif_id
        )
        self.utils.write_file(
            self.utils.hist_path + self.today + ".pkl", notifs_hist
        )
        self.utils.write_file(self.utils.unseen_notif_path, unseen_notifs)

    def get_dunst_hist(self) -> dict:
        return self.utils.get_dunst_hist()

    def get_last_notifs_hist(self) -> tuple[str, list[dict]]:
        return self.utils.get_notifs_history()[0]

    def is_from_yesterday(self, last_notifs_hist_date: str) -> bool:
        yesterday = (self.now - timedelta(days=1)).strftime("%Y-%m-%d")
        if last_notifs_hist_date == yesterday:
            return True
        return False

    def get_last_dunst_notif_id(self, dunst_hist: dict) -> int | None:
        for notif in dunst_hist:
            if notif["category"]["data"] != "trash":
                return notif["id"]["data"]

    def get_last_hist_notif_id(
        self,
        last_notifs_hist: list[dict],
        last_notifs_hist_is_from_yesterday: bool,
    ) -> int:
        if len(last_notifs_hist) != 0:
            return int(last_notifs_hist[0]["id"])
        else:
            if last_notifs_hist_is_from_yesterday:
                notifs = self.utils.get_notifs_history()[1][-1]
                return int(notifs[0]["id"])
            return 0

    def last_dunst_notif_is_new(
        self, last_dunst_notif_id: int, last_hist_notif_id: int
    ) -> bool:
        if last_dunst_notif_id == last_hist_notif_id:
            return False
        return True

    def get_unseen_notifs(self) -> list:
        if self.utils.check_for_unseen_notifs():
            return self.utils.get_unseen_notifs()
        return []

    def get_notif_time(self, notif: dict) -> str:
        notif_time = notif["timestamp"]["data"]
        with open("/proc/uptime", "r") as ut:
            os_uptime_in_secs = float(ut.readline().split()[0])

        time_diff_in_secs = os_uptime_in_secs - float(notif_time) / 1000000
        return (self.now - timedelta(seconds=time_diff_in_secs)).strftime(
            "%H:%M:%S"
        )

    def get_notif_urgency(self, notif: dict) -> str:
        notif_urgency = notif["timeout"]["data"]
        urgency_opts = {3000000: "low", 10000000: "normal", 0: "critical"}
        try:
            return urgency_opts[int(notif_urgency)]
        except (ValueError, KeyError):
            return "normal"

    def update_notifs_lists(
        self,
        dunst_hist: dict,
        notifs_hist: list,
        unseen_notifs: list,
        last_hist_notif_id: int,
    ) -> tuple[list, list]:
        for n, notif in enumerate(dunst_hist):
            notif_id = notif["id"]["data"]
            if notif_id == last_hist_notif_id:
                break
            if notif["category"]["data"] == "trash":
                continue

            time = self.get_notif_time(notif)
            urgency = self.get_notif_urgency(notif)
            message = notif["summary"]["data"]
            submessage = notif["body"]["data"]
            notif_dict = {
                "id": notif_id,
                "time": time,
                "urgency": urgency,
                "message": message,
                "submessage": submessage,
            }
            notifs_hist.insert(n, notif_dict)
            unseen_notifs.insert(n, notif_dict)

        return notifs_hist, unseen_notifs
