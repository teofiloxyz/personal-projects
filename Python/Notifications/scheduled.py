#!/usr/bin/python3


class Scheduled:
    def __init__(self):
        self.now = datetime.now().strftime("%Y-%m-%d")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d")

        self.scheduled_path = "scheduled_path"
        if os.path.exists(self.scheduled_path):
            with open(self.scheduled_path, "rb") as sa:
                (
                    self.calendar_alarms_last_update,
                    self.alarms_list,
                ) = pickle.load(sa)
                self.scheduled_alarms_exist = True
        else:
            self.scheduled_alarms_exist = False

    def show_scheduled_alarms(self, days=366, index=False):
        if not self.scheduled_alarms_exist:
            print("Cannot find the file!")
            return

        if type(days) != "int":
            try:
                days = int(days)
            except ValueError:
                print("Must enter an integer...")
                return

        date_limit = self.now_strp + timedelta(days=days)

        # reversed não muda a variável
        for alarm in reversed(self.alarms_list):
            if datetime.strptime(alarm["date"], "%Y-%m-%d %H:%M") < date_limit:
                if index is False:
                    print(f"{alarm['date']} - {alarm['msg']}")
                else:
                    print(
                        f"[{self.alarms_list.index(alarm) + 1}] "
                        f"{alarm['date']} - {alarm['msg']}"
                    )

    def get_date(self, date=None, use_rofi=False):
        question = (
            "Enter the date for the alarm (e.g.: 12-1-21; 27 = "
            "27-curr.M-curr.Y)"
        )
        if not use_rofi:
            question += ": "
        return qst.get_date(
            question, date_type="%Y-%m-%d", answer=date, use_rofi=use_rofi
        )

    def get_hour(self, hour=None, use_rofi=False):
        question = "Enter the hour of the event " "(e.g.: 9-35; 9 = 9-00)"
        if not use_rofi:
            question += ": "
        return qst.get_hour(
            question, hour_type="%H:%M", answer=hour, use_rofi=use_rofi
        )

    def update_scheduled_alarms(self):
        with open(self.scheduled_path, "wb") as sa:
            pickle.dump(
                [self.calendar_alarms_last_update, self.alarms_list], sa
            )

    def create_alarm(self, msg=None, date=None, hour=None, use_rofi=False):
        if msg is None:
            qst = "Enter the message of the alarm"
            if use_rofi:
                new_alarm_msg = rofi.simple_prompt(qst)
            else:
                new_alarm_msg = input(qst + ": ")
        else:
            new_alarm_msg = msg
        if new_alarm_msg in ("", "q"):
            print("Aborted...")
            return

        if not self.scheduled_alarms_exist:
            print("Cannot find the file!")
            return False

        new_alarm_date = self.get_date(date, use_rofi=use_rofi)
        if new_alarm_date in ("", "q"):
            print("Aborted...")
            return False

        new_alarm_hour = self.get_hour(hour, use_rofi=use_rofi)
        if new_alarm_hour in ("", "q"):
            print("Aborted...")
            return False

        new_alarm_date = new_alarm_date + " " + new_alarm_hour
        new_alarm_date_strp = datetime.strptime(
            new_alarm_date, "%Y-%m-%d %H:%M"
        )
        new_alarm_entry = {
            "uid": "#N/A",
            "date": new_alarm_date,
            "msg": new_alarm_msg,
        }

        if len(self.alarms_list) == 0:
            self.alarms_list.append(new_alarm_entry)
        else:
            for alarm in self.alarms_list:
                alarm_date = alarm["date"]
                alarm_date_strp = datetime.strptime(
                    str(alarm_date), "%Y-%m-%d %H:%M"
                )
                if new_alarm_date_strp <= alarm_date_strp:
                    self.alarms_list.insert(
                        self.alarms_list.index(alarm), new_alarm_entry
                    )
                    break
                elif (
                    new_alarm_date_strp > alarm_date_strp
                    and alarm == self.alarms_list[-1]
                ):
                    self.alarms_list.append(new_alarm_entry)
                    break

        msg = f"New alarm '{new_alarm_msg}' on {new_alarm_date} added!"
        if use_rofi:
            rofi.message(msg)
        else:
            print(msg)
        self.update_scheduled_alarms()

    def remove_alarm(self):
        self.show_scheduled_alarms(index=True)

        while True:
            alarm_index = input("\nChoose the alarm to remove: ")
            if alarm_index == "q":
                print("Aborted...")
                return

            try:
                alarm_index = int(alarm_index) - 1
                self.alarms_list.pop(alarm_index)
                self.update_scheduled_alarms()
                print("Alarm removed!")
                break
            except (ValueError, IndexError):
                print("Invalid answer...")
