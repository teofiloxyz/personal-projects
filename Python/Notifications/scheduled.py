#!/usr/bin/python3
# create_notif func needs division

from Tfuncs import qst, rofi

from datetime import datetime, timedelta

from utils import Utils


class Scheduled:
    def __init__(self) -> None:
        self.utils = Utils()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M")
        (
            self.cal_notifs_last_update,
            self.notifs,
        ) = self.utils.Scheduled().load_file()

    def show(self, days: int = 366, index: bool = False) -> None:
        date_limit = self.now_strp + timedelta(days=days)

        for n, notif in enumerate(reversed(self.notifs), 1):
            if datetime.strptime(notif["date"], "%Y-%m-%d %H:%M") > date_limit:
                continue
            if index:
                print(f"[{n}] {notif['date']} - {notif['msg']}")
                continue
            print(f"{notif['date']} - {notif['msg']}")

    def get_date(self, date: str | None = None, use_rofi: bool = False) -> str:
        question = (
            "Enter the date for the notification (e.g.: 12-1-21; 27 = "
            "27-curr.M-curr.Y)"
        )
        if not use_rofi:
            question += ": "
        return qst.get_date(
            question, date_type="%Y-%m-%d", answer=date, use_rofi=use_rofi
        )

    def get_hour(self, hour: str | None = None, use_rofi: bool = False) -> str:
        question = "Enter the hour of the event (e.g.: 9-35; 9 = 9-00)"
        if not use_rofi:
            question += ": "
        return qst.get_hour(
            question, hour_type="%H:%M", answer=hour, use_rofi=use_rofi
        )

    def create_notif(
        self,
        msg: str = "",
        date: str = "",
        hour: str = "",
        use_rofi: bool = False,
    ):
        if msg != "":
            qst = "Enter the message of the notification"
            if use_rofi:
                new_notif_msg = rofi.simple_prompt(qst)
            else:
                new_notif_msg = input(qst + ": ")
        else:
            new_notif_msg = msg
        if new_notif_msg in ("", "q"):
            print("Aborted...")
            return

        new_notif_date = self.get_date(date, use_rofi=use_rofi)
        if new_notif_date in ("", "q"):
            print("Aborted...")
            return

        new_notif_hour = self.get_hour(hour, use_rofi=use_rofi)
        if new_notif_hour in ("", "q"):
            print("Aborted...")
            return

        new_notif_date += " " + new_notif_hour
        new_notif_date_strp = datetime.strptime(
            new_notif_date, "%Y-%m-%d %H:%M"
        )
        new_notif_entry = {
            "uid": "#N/A",
            "date": new_notif_date,
            "msg": new_notif_msg,
        }

        # fazer func separada
        if len(self.notifs) == 0:
            self.notifs.append(new_notif_entry)
        else:
            for notif in self.notifs:
                notif_date = notif["date"]
                notif_date_strp = datetime.strptime(
                    notif_date, "%Y-%m-%d %H:%M"
                )
                if new_notif_date_strp <= notif_date_strp:
                    self.notifs.insert(
                        self.notifs.index(notif), new_notif_entry
                    )
                    break
                elif (
                    new_notif_date_strp > notif_date_strp
                    and notif == self.notifs[-1]
                ):
                    self.notifs.append(new_notif_entry)
                    break

        msg = f"New notification '{new_notif_msg}' on {new_notif_date} added!"
        if use_rofi:
            rofi.message(msg)
        else:
            print(msg)

        self.utils.Scheduled().write_file(
            self.cal_notifs_last_update, self.notifs
        )

    def remove_notif(self) -> None:
        self.show(index=True)

        while True:
            notif_index = input("\nChoose the notification to remove: ")
            if notif_index == "q":
                print("Aborted...")
                return

            try:
                notif_index = int(notif_index) - 1
                self.notifs.pop(notif_index)
                break
            except (ValueError, IndexError):
                print("Invalid answer...")

        self.utils.Scheduled().write_file(
            self.cal_notifs_last_update, self.notifs
        )
        print("Notification removed!")
