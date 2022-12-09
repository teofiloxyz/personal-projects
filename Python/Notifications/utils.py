#!/usr/bin/python3


class Utils:
    def get_notif_list(pkl_path):
        with open(pkl_path, "rb") as pkl:
            notif_list = pickle.load(pkl)
            notif_list.reverse()
            return notif_list

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

    def get_data(self):
        with open(self.scheduled_path, "rb") as sa:
            self.calendar_alarms_last_update, self.alarms_list = pickle.load(sa)
