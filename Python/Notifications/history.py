from notifs import Notif, Urgency
from database import Query, Edit
from utils import Utils, Date


class History:
    utils = Utils()
    query_db, edit_db = Query(), Edit()

    def show(self, days_delta: int) -> None:
        notifs = self.query_db.get_history(days_delta)
        self.print_all_notifs(notifs)

    def print_all_notifs(self, notifs: list[Notif]) -> None:
        for notif in notifs:
            urgency_color = self.get_urgency_color(notif.urgency)
            row = f"{notif.hour} - {notif.title}: {notif.message}"
            print(urgency_color + row + "\033[0m")

    def get_urgency_color(self, urgency: Urgency) -> str:
        urgency_colors = {
            Urgency.LOW: "\033[32m",  # green
            Urgency.NORMAL: "\033[33m",  # yellow
            Urgency.CRITICAL: "\033[31m",  # red
        }
        return urgency_colors[urgency]

    def show_unseen_notifs(self, resend_notifs: bool = False) -> None:
        unseen_notifs = self.query_db.get_all_unseen()
        if not unseen_notifs:
            print("No new notifications...")
            return
        print("NEW:")
        self.print_all_notifs(unseen_notifs)

        if resend_notifs:
            [
                self.utils.send_notification(
                    notif.title,
                    notif.message,
                    notif.urgency,
                    category="trash",
                    muted=True,
                )
                for notif in unseen_notifs
            ]
        self.edit_db.remove_all_from_unseen()


class UpdaterDaemon:
    utils, date = Utils(), Date()
    edit_db = Edit()

    # Improve design
    def start(self) -> None:
        current_notifs, sender_num = dict(), "0"
        cmd = "dbus-monitor interface='org.freedesktop.Notifications'"
        for line in self.utils.shell_generator(cmd):
            line = " ".join(line.split())
            if line.startswith("method call time="):
                # Notification started
                sender_num = self.get_notif_sender_num(line)
                notif_unix_time = self.get_notif_unix_time(line)
                current_notifs = self.update_current_notifs(
                    current_notifs, sender_num, notif_unix_time
                )
            elif line.startswith("signal time="):
                # Notification ended
                destination_num = self.get_notif_destination_num(line)
                if destination_num not in current_notifs.keys():
                    continue
                notif = self.create_notif(current_notifs, destination_num)
                if notif.category != "trash":
                    self.save_notif(notif)
                del current_notifs[destination_num]
                sender_num = "0"
            else:
                # All the stuff between the start and the end of the notif
                if sender_num == "0":
                    continue
                current_notifs[sender_num]["body"].append(line)

    def get_notif_sender_num(self, line: str) -> str:
        return self.utils.extract_substr_from_str("sender=:(.+) ->", line, "0")

    def get_notif_unix_time(self, line: str) -> int:
        time = self.utils.extract_substr_from_str(
            "time=(.[0-9]+)\\.", line, "0"
        )
        return int(time)

    def update_current_notifs(
        self, current_notifs: dict, sender_num: str, notif_unix_time: int
    ) -> dict:
        current_notifs[sender_num] = dict()
        current_notifs[sender_num]["body"] = list()
        current_notifs[sender_num]["unix_time"] = notif_unix_time
        return current_notifs

    def get_notif_destination_num(self, line: str) -> str:
        return self.utils.extract_substr_from_str(
            "destination=:(.+) serial=", line, "error"
        )

    def create_notif(self, current_notifs: dict, destination_num: str) -> Notif:
        notif_body = current_notifs[destination_num]["body"]
        notif_unix_time = current_notifs[destination_num]["unix_time"]
        date, hour = self.get_notif_full_date(notif_unix_time).split()
        return Notif(
            date=date,
            hour=hour,
            title=self.get_notif_title(notif_body),
            message=self.get_notif_message(notif_body),
            urgency=self.get_notif_urgency(notif_body),
            category=self.get_notif_category(notif_body),
        )

    def get_notif_full_date(self, unix_time: float) -> str:
        return self.date.get_date_from_unix_time(unix_time)

    def get_notif_title(self, body: list) -> str:
        return self.utils.extract_substr_from_str('string "(.*)"', body[3])

    def get_notif_message(self, body: list) -> str:
        return self.utils.extract_substr_from_str('string "(.*)"', body[4])

    def get_notif_urgency(self, body: list) -> Urgency:
        index = body.index('string "urgency"')
        urgency_int = body[index + 1][-1]
        urgs = [Urgency.LOW, Urgency.NORMAL, Urgency.CRITICAL]
        return urgs[int(urgency_int)]

    def get_notif_category(self, body: list) -> str:
        if 'string "category"' in body:
            index = body.index('string "category"')
            category = body[index + 1]
            return self.utils.extract_substr_from_str(
                'variant string "(.*)"', category
            )
        return ""

    def save_notif(self, notif: Notif) -> None:
        self.edit_db.add_to_history(notif)
        self.edit_db.add_to_unseen(notif)
