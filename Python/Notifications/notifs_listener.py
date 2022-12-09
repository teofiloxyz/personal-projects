#!/usr/bin/python3
# Should be triggered every minute

from datetime import datetime

from utils import Utils


class NotifsListener:
    def main(self):
        if self.check_file() is False:
            return
        self.get_data()
        self.need_update, self.notif_is_mute = False, False
        while True:
            if self.check_next_alarm() is False:
                break
            self.send_notification()
            self.need_update, self.notif_is_mute = True, True
        if self.need_update:
            self.update_file()

    def check_next_alarm(self):
        if len(self.alarms_list) == 0:
            return False
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d %H:%M")
        self.next_alarm = self.alarms_list[0]
        self.next_alarm_date = self.next_alarm["date"]
        self.next_alarm_date_strp = datetime.strptime(
            self.next_alarm_date, "%Y-%m-%d %H:%M"
        )
        if self.now_strp < self.next_alarm_date_strp:
            return False
        else:
            self.notif = self.next_alarm["msg"]
            self.alarms_list.pop(0)
