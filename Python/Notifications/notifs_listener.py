#!/usr/bin/python3
# Should be triggered every minute

import os
import subprocess
import pickle
from datetime import datetime


class NotifsListener:
    def __init__(self):
        self.scheduled_path = "scheduled_path"
        self.notif_sound = "notif_sound"

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

    def check_file(self):
        if not os.path.exists(self.scheduled_path):
            self.calendar_alarms_last_update, self.alarms_list = (
                "2000-01-01 00:00:00",
                [],
            )
            self.update_file()
            return False

    def get_data(self):
        with open(self.scheduled_path, "rb") as sa:
            self.calendar_alarms_last_update, self.alarms_list = pickle.load(sa)

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

    def send_notification(self):
        cmd = (
            f'paplay {self.notif_sound} & notify-send "{self.notif}"'
            if not self.notif_is_mute
            else f'notify-send "{self.notif}"'
        )
        subprocess.run(cmd, shell=True)

    def update_file(self):
        with open(self.scheduled_path, "wb") as sa:
            pickle.dump(
                [self.calendar_alarms_last_update, self.alarms_list], sa
            )


AlarmsListener().main()
