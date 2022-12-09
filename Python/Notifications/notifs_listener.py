#!/usr/bin/python3
# Should be triggered every minute
# Improve main func design

from datetime import datetime

from utils import Utils


class NotifsListener:
    def __init__(self) -> None:
        self.utils = Utils()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M")

    def main(self) -> None:
        cal_notifs_last_update, notifs = self.utils.Scheduled().load_file()
        if len(notifs) == 0:
            return

        file_needs_update, notif_is_muted = False, False
        for notif in notifs:
            notif_date = self.get_notification_date(notif)
            if not self.notification_is_due(notif_date):
                return
            self.utils.send_notification(notif["msg"], muted=notif_is_muted)
            notifs.pop(0)
            file_needs_update, notif_is_muted = True, True

        if file_needs_update:
            self.utils.Scheduled().write_file(cal_notifs_last_update, notifs)

    def get_notification_date(self, notif: dict) -> datetime:
        notif_date = notif["date"]
        return datetime.strptime(notif_date, "%Y-%m-%d %H:%M")

    def notification_is_due(self, notif_date: datetime) -> bool:
        if self.now_strp < notif_date:
            return True
        return False
