from Tfuncs import fcol, ffmt

from utils import Utils, Notif


# clean this
class History:
    utils = Utils().History()
    notifs_history = utils.get_notifs_history()

    @staticmethod
    def updater_daemon() -> None:
        UpdaterDaemon().main()

    def show_unseen_notifs(self) -> None:
        if not self.utils.check_for_notifs_file(self.utils.unseen_notif_path):
            print("No new notifications...")
            return

        unseen_notifs = self.utils.get_unseen_notifs()
        self.utils.remove_unseen_notifs()

        print(f"{ffmt.bold}{fcol.red}NEW:{ffmt.reset}")
        print(
            *(
                f"{notif.date} - {notif.title}: {notif.message}"
                for notif in unseen_notifs
            ),
            sep="\n",
        )

    def show_all(self) -> None:
        for day in sorted(self.notifs_history):
            print(
                *(
                    f"{notif.date} - {notif.title}: {notif.message}"
                    for notif in day
                ),
                sep="\n",
            )

    def show_all_filter_urg(self, urgency: str) -> None:
        urg_colors = {
            "low": fcol.green,
            "normal": fcol.yellow,
            "critical": fcol.red,
        }
        col = urg_colors[urgency]
        print(
            f"Showing all{ffmt.bold}{col} "
            f"{urgency} urgency{ffmt.reset} past notifications"
        )

        for day in sorted(self.notifs_history):
            notifs = [
                f"{notif.date} - {notif.title}: {notif.message}"
                for notif in day
                if notif.urgency == urgency
            ]
            if len(notifs) == 0:
                print("None")
            else:
                print("\n".join(notifs))


class UpdaterDaemon:
    utils = Utils()

    # Improve design
    def main(self) -> None:
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
        return self.utils.extract_str_from_substr("sender=:(.+) ->", line, "0")

    def get_notif_unix_time(self, line: str) -> int:
        time = self.utils.extract_str_from_substr("time=(.[0-9]+)\.", line, "0")
        return int(time)

    def update_current_notifs(
        self, current_notifs: dict, sender_num: str, notif_unix_time: int
    ) -> dict:
        current_notifs[sender_num] = dict()
        current_notifs[sender_num]["body"] = list()
        current_notifs[sender_num]["unix_time"] = notif_unix_time
        return current_notifs

    def get_notif_destination_num(self, line: str) -> str:
        return self.utils.extract_str_from_substr(
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
        return self.utils.get_date_from_unix_time(unix_time)

    def get_notif_title(self, body: list) -> str:
        return self.utils.extract_str_from_substr('string "(.*)"', body[3])

    def get_notif_message(self, body: list) -> str:
        return self.utils.extract_str_from_substr('string "(.*)"', body[4])

    def get_notif_urgency(self, body: list) -> str:
        index = body.index('string "urgency"')
        urgency_int = body[index + 1][-1]
        urgs = ["low", "normal", "critical"]
        return urgs[int(urgency_int)]

    def get_notif_category(self, body: list) -> str:
        if 'string "category"' in body:
            index = body.index('string "category"')
            category = body[index + 1]
            return self.utils.extract_str_from_substr(
                'variant string "(.*)"', category
            )
        return ""

    def save_notif(self, notif: Notif) -> None:
        unseen_notifs = self.utils.History().get_unseen_notifs()
        notifs_hist, hist_path = self.utils.History().get_today_notifs_history()
        unseen_notifs.append(notif)
        notifs_hist.append(notif)
        self.utils.History().save_unseen_notifs(unseen_notifs)
        self.utils.History().save_today_notifs_history(notifs_hist, hist_path)
