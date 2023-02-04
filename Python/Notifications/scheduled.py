from Tfuncs import Rofi

import copy
from typing import Optional

from notifs import Notif
from database import Query, Edit
from utils import Utils, Date


class Scheduled:
    utils, date = Utils(), Date()
    rofi = Rofi()
    query_db, edit_db = Query(), Edit()

    def show(self, days_delta: int, show_index: bool = False) -> None:
        notifs = self.query_db.get_scheduled(days_delta)
        for n, notif in enumerate(notifs, 1):
            entry = f"{notif.date} {notif.hour} - {notif.message}"
            if show_index:
                entry = f"[{n}] " + entry
            print(entry)

    def create_notif(
        self,
        message: Optional[str] = None,
        date: Optional[str] = None,
        hour: Optional[str] = None,
        use_rofi: bool = False,
    ) -> None:
        message = self._get_notif_message(message, use_rofi)
        if message == "q":
            print("Aborting...")
            return

        date = self._get_notif_date(date, use_rofi)
        if not date:
            print("Aborting...")
            return

        hour = self._get_notif_hour(hour, use_rofi)
        if not hour:
            print("Aborting...")
            return

        notif = Notif(date=date, hour=hour, title="Scheduled", message=message)
        self.edit_db.add_to_scheduled(notif)
        self._show_schedule_message(notif, use_rofi)

    def _get_notif_message(self, message: Optional[str], use_rofi: bool) -> str:
        if message is not None:
            return message
        question = "Enter the message of the notification"
        return (
            self.rofi.simple_prompt(question)
            if use_rofi
            else input(question + ": ")
        )

    def _get_notif_date(
        self, date: Optional[str], use_rofi: bool
    ) -> Optional[str]:
        question = (
            "Enter the date for the notification (e.g.: 12-1-21; 27 = "
            "27-curr.M-curr.Y)"
        )
        return self.date.prompt_date(
            question, date_type="%Y-%m-%d", answer=date, use_rofi=use_rofi
        )

    def _get_notif_hour(
        self, hour: Optional[str], use_rofi: bool
    ) -> Optional[str]:
        question = "Enter the hour of the event (e.g.: 9-35; 9 = 9-00)"
        return self.date.prompt_hour(
            question, hour_type="%H:%M:%S", answer=hour, use_rofi=use_rofi
        )

    def _show_schedule_message(self, notif: Notif, use_rofi: bool) -> None:
        msg = (
            f"New notification '{notif.message}' on {notif.date} "
            f"at {notif.hour} added!"
        )
        self.rofi.message_box(msg) if use_rofi else print(msg)

    def remove_notif(self) -> None:  # improve
        notifs = self.query_db.get_scheduled(365)
        self.show(days_delta=365, show_index=True)
        prompt = input(
            "\nChoose the notification to remove or several (e.g.: 30+4+43): "
        )
        if prompt == "q":
            print("Aborting...")
            return

        for index in prompt.split("+"):
            try:
                notif = notifs[int(index) - 1]
                self.edit_db.remove_from_scheduled(notif)
            except (ValueError, IndexError):
                print("Invalid input...\nAborting...")
                return

    def edit_notif(self) -> None:  # improve
        notifs = self.query_db.get_scheduled(365)
        self.show(days_delta=365, show_index=True)
        prompt = input("\nChoose the notification to edit: ")
        if prompt == "q":
            print("Aborting...")
            return
        try:
            notif = notifs[int(prompt) - 1]
        except (ValueError, IndexError):
            print("Invalid input...\nAborting...")
            return

        new_notif = copy.copy(notif)
        while True:
            prompt = input("\n:: Edit what: message or time [M/t] ")
            if prompt == "q":
                print("Aborting...")
                return
            elif prompt in ("", "M", "m"):
                message = self._edit_notif_message(notif)
                if message == "q":
                    print("Aborting...")
                    return
                new_notif.message = message
                break
            elif prompt in ("T", "t"):
                full_date = self._edit_notif_full_date(notif)
                if not full_date:
                    print("Aborting...")
                    return
                new_notif.date, new_notif.hour = full_date.split()
                break

        self.edit_db.update_on_scheduled(notif, new_notif)

    def _edit_notif_message(self, notif: Notif) -> str:
        print(f"Current message: {notif.message}")
        return self._get_notif_message(message=None, use_rofi=False)

    def _edit_notif_full_date(self, notif: Notif) -> Optional[str]:
        print(f"Current full date: {notif.date} {notif.hour}")
        date = self._get_notif_date(date=None, use_rofi=False)
        if not date:
            return None
        hour = self._get_notif_hour(hour=None, use_rofi=False)
        if not hour:
            return None
        return date + " " + hour


# Should be triggered every minute or so
class NotifSender:
    utils, date = Utils(), Date()
    query_db, edit_db = Query(), Edit()
    now = date.get_date_now()
    now_strp = date.get_date_strp(now)

    def main(self) -> None:
        notifs = self.query_db.get_scheduled(1)
        if len(notifs) == 0:
            return

        notif_is_muted = False
        for notif in notifs:
            if not self._notification_is_due(notif):
                continue
            self._send_notification(notif, notif_is_muted)
            self.edit_db.remove_from_scheduled(notif)
            notif_is_muted = True

    def _notification_is_due(self, notif: Notif) -> bool:
        notif_full_date = f"{notif.date} {notif.hour}"
        if self.now_strp >= self.date.get_date_strp(notif_full_date):
            return True
        return False

    def _send_notification(self, notif: Notif, notif_is_muted: bool) -> None:
        self.utils.send_notification(
            title=notif.title,
            message=notif.message,
            urgency=notif.urgency,
            category=notif.category,
            muted=notif_is_muted,
        )
