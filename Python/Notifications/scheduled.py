from Tfuncs import qst, rofi

from utils import Utils, Notif


# add edit option
class Scheduled:
    utils = Utils()
    notifs = utils.Scheduled().get_scheduled_notifs()

    def show(self, days: int = 366, show_index: bool = False) -> None:
        date_limit_strp = self.utils.get_date_limit_strp(days)
        for n, notif in enumerate(reversed(self.notifs), 1):
            notif_full_date = f"{notif.date} {notif.hour}"
            if self.utils.get_date_strp(notif_full_date) > date_limit_strp:
                continue
            entry = f"{notif.date} {notif.hour} - {notif.message}"
            if show_index:
                entry = f"[{n}] " + entry
            print(entry)

    def create_notif(
        self,
        message: str | None = None,
        date: str | None = None,
        hour: str | None = None,
        use_rofi: bool = False,
    ) -> None:
        message = self.get_notif_message(message, use_rofi)
        if message == "q":
            print("Aborting...")
            return

        date = self.get_notif_date(date, use_rofi)
        if date == "q":
            print("Aborting...")
            return

        hour = self.get_notif_hour(hour, use_rofi)
        if hour == "q":
            print("Aborting...")
            return

        notif = Notif(date=date, hour=hour, title="Scheduled", message=message)
        self.save_notif(notif)
        self.show_schedule_message(notif, use_rofi)

    def get_notif_message(self, message: str | None, use_rofi: bool) -> str:
        if message is not None:
            return message
        question = "Enter the message of the notification"
        return (
            rofi.simple_prompt(question) if use_rofi else input(question + ": ")
        )

    def get_notif_date(self, date: str | None, use_rofi: bool) -> str:
        question = (
            "Enter the date for the notification (e.g.: 12-1-21; 27 = "
            "27-curr.M-curr.Y)"
        )
        return qst.get_date(
            question, date_type="%Y-%m-%d", answer=date, use_rofi=use_rofi
        )

    def get_notif_hour(self, hour: str | None, use_rofi: bool) -> str:
        question = "Enter the hour of the event (e.g.: 9-35; 9 = 9-00)"
        return qst.get_hour(
            question, hour_type="%H:%M:%S", answer=hour, use_rofi=use_rofi
        )

    def save_notif(self, notif: Notif) -> None:
        self.notifs.append(notif)
        self.order_notifs()
        self.utils.Scheduled().save_scheduled_notifs(self.notifs)

    def order_notifs(self) -> None:
        self.notifs = sorted(
            self.notifs, key=lambda notif: (notif.date + notif.hour)
        )

    def show_schedule_message(self, notif: Notif, use_rofi: bool) -> None:
        msg = (
            f"New notification '{notif.message}' on {notif.date} "
            f"at {notif.hour} added!"
        )
        rofi.message(msg) if use_rofi else print(msg)

    def remove_notif(self) -> None:
        # Improve design
        self.show(show_index=True)
        while True:
            prompt = input(
                "\nChoose the notification to remove or "
                "several (e.g.: 30+4+43): "
            )
            if prompt == "q":
                print("Aborting...")
                return

            nindex = prompt.split("+")
            nindex = [self.correct_notif_index(x) for x in nindex]
            if None not in nindex:
                break

        [self.notifs.pop(x) for x in nindex]
        self.utils.Scheduled().save_scheduled_notifs(self.notifs)

    def correct_notif_index(self, index: str) -> int | None:
        try:
            index = int(index) - 1
            self.notifs[index]
            return index
        except ValueError:
            print("Enter an integer...")
        except IndexError:
            print(f"Index {index} not found on notifs list...")
        return None


# Should be triggered every minute or so
class ScheduledNotifsListener:  # Need a better class name
    utils = Utils()
    notifs = utils.Scheduled().get_scheduled_notifs()
    now = utils.get_date_now()
    now_strp = utils.get_date_strp(now)

    def main(self) -> None:
        if len(self.notifs) == 0:
            return

        notif_is_muted, update_file = False, False
        for notif in list(self.notifs):  # Need a copy to not mess up the loop
            if not self.notification_is_due(notif):
                break
            self.send_notification(notif, notif_is_muted)
            self.notifs.pop(0)
            notif_is_muted, update_file = True, True

        if update_file:
            self.utils.Scheduled().save_scheduled_notifs(self.notifs)

    def notification_is_due(self, notif: Notif) -> bool:
        notif_full_date = f"{notif.date} {notif.hour}"
        if self.now_strp >= self.utils.get_date_strp(notif_full_date):
            return True
        return False

    def send_notification(self, notif: Notif, notif_is_muted: bool) -> None:
        self.utils.send_notification(
            title=notif.title,
            message=notif.message,
            urgency=notif.urgency,
            category=notif.category,
            muted=notif_is_muted,
        )
