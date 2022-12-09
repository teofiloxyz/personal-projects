#!/usr/bin/python3
"""Deve ser usado após a criação/edição de eventos no calendário,
de modo a criar alarmes no ficheiro de scheduled."""

import os
import pickle
from datetime import datetime, timedelta


class CalendarNotifs:
    def __init__(self):
        self.scheduled_path = "scheduled_path"
        self.cals_path = "calendars_path"

    def main(self):
        if self.check_alarms_file() is False:
            self.update_file()
            return
        self.get_alarms_file_data()
        self.get_cal_files_list()
        for self.cal_file in self.cal_files_list:
            self.append_cal_file_uid()
            """ Para os calendários recurrentes:
            Caso o evento já tenha passado e o ficheiro não seja recente,
            volta a criar um novo evento para a próxima data,
            de acordo com a respetiva recurrência"""
            is_rec_and_past = (
                "personal" not in self.cal_file
                and self.cal_file_uid not in self.alarms_uids_list
            )
            if self.check_if_new() is True or is_rec_and_past is True:
                if self.cal_file_uid in self.alarms_uids_list:
                    # Acaba por ser modificado, ao apagar e criar um novo
                    self.delete_event_alarms()
                # Caso o evento ñ tenha alarmes
                if self.get_cal_file_info() is False:
                    continue
                for alarm in self.cal_event_alarms_list:
                    # Caso a data do alarme tenha passado
                    if self.get_alarm_date_and_msg(alarm) is False:
                        continue
                    self.create_alarm()
        self.check_if_cal_file_deleted()
        self.cal_alarms_last_update = self.now
        self.update_file()

    def check_alarms_file(self):
        if not os.path.exists(self.scheduled_path):
            self.cal_alarms_last_update, self.alarms_list = (
                "2000-01-01 00:00:00",
                [],
            )
            return False

    def get_alarms_file_data(self):
        with open(self.scheduled_path, "rb") as sa:
            self.cal_alarms_last_update, self.alarms_list = pickle.load(sa)

        self.cal_alarms_last_update_strp = datetime.strptime(
            self.cal_alarms_last_update, "%Y-%m-%d %H:%M:%S"
        )
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d %H:%M:%S")
        self.alarms_uids_list = [alarm["uid"] for alarm in self.alarms_list]
        self.cals_uids_list = []

    def get_cal_files_list(self):
        self.cal_files_list = [
            os.path.join(root_dirs_files[0], file)
            for root_dirs_files in os.walk(self.cals_path)
            for file in root_dirs_files[2]
        ]

    def append_cal_file_uid(self):
        self.cal_file_uid = os.path.basename(self.cal_file).split(".")[0]
        self.cals_uids_list.append(self.cal_file_uid)

    def check_if_new(self):
        cal_file_modif_date = os.path.getmtime(self.cal_file)
        cal_file_modif_date = datetime.fromtimestamp(
            cal_file_modif_date
        ).strftime("%Y-%m-%d %H:%M:%S")

        cal_file_modif_date_strp = datetime.strptime(
            cal_file_modif_date, "%Y-%m-%d %H:%M:%S"
        )
        if cal_file_modif_date_strp > self.cal_alarms_last_update_strp:
            return True

    def delete_event_alarms(self):
        # Plural because one cal event might have several alarms
        self.alarms_list = [
            alarm
            for alarm in self.alarms_list
            if alarm["uid"] != self.cal_file_uid
        ]

    def get_cal_file_info(self):
        with open(self.cal_file, "r") as cf:
            cal_file_info = cf.readlines()

        self.cal_event_alarms_list, allow_dtstart, self.recurrent_event = (
            [],
            False,
            False,
        )

        for line in cal_file_info:
            line = line.strip("\n")
            if line == "BEGIN:VEVENT":
                allow_dtstart = True
                continue
            if allow_dtstart is True and line.startswith("DTSTART"):
                self.cal_event_date = line.split(":")[-1]
                allow_dtstart = False
                continue
            if line.startswith("TRIGGER"):
                self.cal_event_alarms_list.append(line.split(":")[-1])
                continue
            if line.startswith("SUMMARY"):
                line = line.replace("\\", "")
                self.new_alarm_msg = line[8:]
                continue

            """ personal é mesmo para evitar um bug onde, por vezes,
            os personal events têm rrule, e não é suposto,
            porque nunca são recurrentes. """
            if line.startswith("RRULE") and "personal" not in self.cal_file:
                self.recurrent_event = True
                self.new_alarm_recurrency = line.split("=")[-1]

        if len(self.cal_event_alarms_list) == 0:
            return False

    def get_alarm_date_and_msg(self, alarm):
        # P = alarm_date >= event_date; -P reverse
        alarm_time_positive = True if alarm[0] == "P" else False
        alarm = alarm.strip("-P")
        # if time is in (H or M or S) or just a date
        alarm_time_type_HMS = True if alarm[0] == "T" else False
        alarm = alarm.strip("T")
        # some dates don't have the hours
        t_format = "%Y%m%dT%H%M%S" if "T" in self.cal_event_date else "%Y%m%d"
        cal_event_date = datetime.strptime(self.cal_event_date, t_format)

        msg_appendix, alarm_time_secs = "", 0
        alarm_time_type, alarm_time = alarm[-1], alarm[:-1]
        if alarm_time == "0":
            msg_appendix = " (now)"
            alarm_time_secs = 0
            self.new_alarm_date = cal_event_date
        else:
            if alarm_time_type_HMS:
                if alarm_time_type == "S":
                    msg_appendix = f" (in {alarm_time} seconds)"
                    alarm_time_secs = 1 * int(alarm_time)
                elif alarm_time_type == "M":
                    msg_appendix = f" (in {alarm_time} minutes)"
                    alarm_time_secs = 60 * int(alarm_time)
                elif alarm_time_type == "H":
                    msg_appendix = f" (in {alarm_time} hours)"
                    alarm_time_secs = 3600 * int(alarm_time)
            else:
                if alarm_time_type == "D":
                    msg_appendix = f" (in {alarm_time} days)"
                    alarm_time_secs = 86400 * int(alarm_time)
                elif alarm_time_type == "W":
                    msg_appendix = f" (in {alarm_time} weeks)"
                    alarm_time_secs = 604800 * int(alarm_time)
                elif alarm_time_type == "M":
                    msg_appendix = f" (in {alarm_time} months)"
                    alarm_time_secs = 2592000 * int(alarm_time)
            if not alarm_time_positive:
                self.new_alarm_date = cal_event_date - timedelta(
                    seconds=alarm_time_secs
                )
                # singular
                if alarm_time == "1":
                    msg_appendix = msg_appendix[:-2] + ")"
            else:
                self.new_alarm_date = cal_event_date + timedelta(
                    seconds=alarm_time_secs
                )
                msg_appendix = ""

        if self.recurrent_event:
            while self.now_strp > self.new_alarm_date:
                if self.new_alarm_recurrency == "YEARLY":
                    self.new_alarm_date = self.new_alarm_date.replace(
                        year=self.new_alarm_date.year + 1
                    )
                elif self.new_alarm_recurrency == "MONTHLY":
                    self.new_alarm_date = self.new_alarm_date.replace(
                        month=self.new_alarm_date.month + 1
                    )
                elif self.new_alarm_recurrency == "WEEKLY":
                    self.new_alarm_date = self.new_alarm_date + timedelta(
                        days=7
                    )

        if self.now_strp > self.new_alarm_date:
            return False
        self.new_alarm_msg_total = self.new_alarm_msg + msg_appendix

    def create_alarm(self):
        self.alarms_uids_list.append(self.cal_file_uid)
        new_alarm_entry = {
            "uid": self.cal_file_uid,
            "date": datetime.strftime(self.new_alarm_date, "%Y-%m-%d %H:%M"),
            "msg": self.new_alarm_msg_total,
        }

        if len(self.alarms_list) == 0:
            self.alarms_list.append(new_alarm_entry)
            return

        new_alarm_date_strp = datetime.strptime(
            str(self.new_alarm_date), "%Y-%m-%d %H:%M:%S"
        )
        for alarm in self.alarms_list:
            alarm_date = alarm["date"]
            alarm_date_strp = datetime.strptime(
                str(alarm_date), "%Y-%m-%d %H:%M"
            )
            if new_alarm_date_strp <= alarm_date_strp:
                self.alarms_list.insert(
                    self.alarms_list.index(alarm), new_alarm_entry
                )
                return
            elif (
                new_alarm_date_strp > alarm_date_strp
                and alarm == self.alarms_list[-1]
            ):
                self.alarms_list.append(new_alarm_entry)
                return

    def check_if_cal_file_deleted(self):
        # N/A é para os alarms criados manualmente fora de eventos de calendar
        self.alarms_list = [
            alarm
            for alarm in self.alarms_list
            if alarm["uid"] in self.cals_uids_list or alarm["uid"] == "#N/A"
        ]

    def update_file(self):
        with open(self.scheduled_path, "wb") as sa:
            pickle.dump([self.cal_alarms_last_update, self.alarms_list], sa)


CalendarAlarms().main()
