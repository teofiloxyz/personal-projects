#!/usr/bin/python3
"""Deve ser usado após a criação/edição de eventos no calendário,
de modo a criar notificações no ficheiro de scheduled."""

import os
from datetime import datetime, timedelta

from utils import Utils


class CalendarNotifs:
    utils = Utils().Scheduled()
    cals_path = "calendars_path"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    (
        cal_notifs_last_update,
        notifs,
    ) = utils.load_file()

    def main(self) -> None:
        cal_notifs_last_update, notifs = self.get_notifs_info()
        cal_notifs_last_update_strp = self.get_date_strp(cal_notifs_last_update)

        notifs_uids = self.get_notifs_uids(notifs)
        cals_uids = list()

        cal_files = self.get_cal_files(self.cals_path)
        for cal_file in cal_files:
            cal_file_uid = self.get_cal_file_uid(cal_file)
            cals_uids.append(cal_file_uid)

            is_rec_and_past = self.check_if_rec_and_past(
                cal_file, cal_file_uid, notifs_uids
            )
            cal_file_modif_date = self.get_cal_file_modif_date(cal_file)
            cal_file_modif_date_strp = self.get_date_strp(cal_file_modif_date)
            is_new = self.check_if_new(
                cal_file_modif_date_strp, cal_notifs_last_update_strp
            )
            if not is_rec_and_past and not is_new:
                continue

            if cal_file_uid in notifs_uids:
                # Acaba por ser modificado, ao apagar e criar nova(s)
                notifs = self.delete_event_notifs(cal_file_uid, notifs)

            cal_file_lines = self.get_file_lines(cal_file)
            (
                cal_event_date,
                cal_event_notifs,
                notif_msg,
                event_is_recurrent,
                event_recurrency,
            ) = self.get_cal_file_info(cal_file, cal_file_lines)
            cal_event_date_format = self.get_cal_event_date_format(
                cal_event_date
            )
            cal_event_date_strp = self.get_date_strp(
                cal_event_date, cal_event_date_format
            )
            cal_file_has_notifs = self.check_if_cal_file_has_notifs(
                cal_event_notifs
            )
            if not cal_file_has_notifs:
                continue

            for notif in cal_event_notifs:
                notif_delay_is_negative = self.check_if_notif_delay_is_negative(
                    notif
                )
                notif = notif.strip("-P")
                notif_time_has_HMS = self.check_if_notif_time_has_HMS(notif)
                notif = notif.strip("T")
                notif_time_type, notif_delay = notif[-1], notif[:-1]
                (
                    notif_msg_appendix,
                    notif_delay_secs,
                ) = self.get_notif_msg_appendix_and_delay(
                    notif_delay, notif_time_type, notif_time_has_HMS
                )

                if notif_delay == "1":
                    notif_msg_appendix = notif_msg_appendix[:-2] + ")"

                if notif_delay_is_negative:
                    notif_date_strp = self.get_notif_date(
                        notif_delay_secs,
                        cal_event_date_strp,
                        notif_delay_is_negative,
                    )
                else:
                    notif_date_strp = self.get_notif_date(
                        notif_delay_secs,
                        cal_event_date_strp,
                        notif_delay_is_negative,
                    )
                    notif_msg_appendix = ""

                if event_is_recurrent:
                    self.correct_recurrent_date(
                        notif_date_strp, event_recurrency
                    )

                if self.check_if_notif_date_already_passed(notif_date_strp):
                    continue

                notifs_uids.append(cal_file_uid)
                notif_entry = self.create_notif_entry(
                    cal_file_uid, notif_date_strp, notif_msg, notif_msg_appendix
                )
                notifs = self.schedule_notif(
                    notifs, notif_entry, notif_date_strp
                )

        notifs = self.refresh_notifs(notifs, cals_uids)
        cal_notifs_last_update = self.now
        self.utils.write_file(cal_notifs_last_update, notifs)

    def get_notifs_info(self) -> tuple[str, list]:
        return self.utils.load_file()

    def get_date_strp(
        self, date: str, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        return datetime.strptime(date, date_format)

    def get_notifs_uids(self, notifs: list) -> list:
        return [notif["uid"] for notif in notifs]

    def get_cal_files(self, cals_path: str) -> list[str]:
        return [
            os.path.join(root_dirs_files[0], file)
            for root_dirs_files in os.walk(cals_path)
            for file in root_dirs_files[2]
        ]

    def get_cal_file_uid(self, cal_file: str) -> str:
        return os.path.basename(cal_file).split(".")[0]

    def check_if_rec_and_past(
        self, cal_file: str, cal_file_uid: str, notifs_uids: list[str]
    ) -> bool:
        """Para os calendários recurrentes: Caso o evento já tenha passado
        e o ficheiro não seja recente, volta a criar um novo evento para
        a próxima data, de acordo com a respetiva recurrência"""

        return "personal" not in cal_file and cal_file_uid not in notifs_uids

    def get_cal_file_modif_date(self, cal_file: str) -> str:
        cal_file_modif_date = os.path.getmtime(cal_file)
        return datetime.fromtimestamp(cal_file_modif_date).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def check_if_new(
        self,
        cal_file_modif_date_strp: datetime,
        cal_notifs_last_update_strp: datetime,
    ) -> bool:
        if cal_file_modif_date_strp > cal_notifs_last_update_strp:
            return True
        return False

    def delete_event_notifs(
        self, cal_file_uid: str, notifs: list[dict]
    ) -> list[dict]:
        """Plural because one cal event can have several scheduled notifs"""
        return [notif for notif in notifs if notif["uid"] != cal_file_uid]

    def get_file_lines(self, file: str) -> list[str]:
        with open(file, "r") as cf:
            return cf.readlines()

    def get_cal_file_info(
        self, cal_file: str, cal_file_lines: list[str]
    ) -> tuple:
        # needs rework
        (
            cal_event_date,
            cal_event_notifs,
            notif_msg,
            event_is_recurrent,
            event_recurrency,
            allow_dtstart,
        ) = (
            None,
            list(),
            None,
            False,
            None,
            False,
        )

        for line in cal_file_lines:
            line = line.strip("\n")
            if line == "BEGIN:VEVENT":
                allow_dtstart = True
                continue
            if allow_dtstart and line.startswith("DTSTART"):
                cal_event_date = line.split(":")[-1]
                allow_dtstart = False
                continue
            if line.startswith("TRIGGER"):
                cal_event_notifs.append(line.split(":")[-1])
                continue
            if line.startswith("SUMMARY"):
                line = line.replace("\\", "")
                notif_msg = line[8:]
                continue
            """ personal é mesmo para evitar um "bug" onde, por vezes,
            os personal events têm rrule, e não é suposto,
            porque nunca são recurrentes. """
            if line.startswith("RRULE") and "personal" not in cal_file:
                event_is_recurrent = True
                event_recurrency = line.split("=")[-1]

        return (
            cal_event_date,
            cal_event_notifs,
            notif_msg,
            event_is_recurrent,
            event_recurrency,
        )

    def check_if_cal_file_has_notifs(self, cal_event_notifs: list) -> bool:
        if len(cal_event_notifs) == 0:
            return False
        return True

    def check_if_notif_delay_is_negative(self, notif: str) -> bool:
        """P = notif_date >= event_date; -P reverse
        notif time relative to the cal event date"""

        return False if notif[0] == "P" else True

    def check_if_notif_time_has_HMS(self, notif: str) -> bool:
        """If time is in (H or M or S) or just a date"""

        return True if notif[0] == "T" else False

    def get_cal_event_date_format(self, cal_event_date: str) -> str:
        """Some dates don't have the hours"""

        return "%Y%m%dT%H%M%S" if "T" in cal_event_date else "%Y%m%d"

    def get_notif_msg_appendix_and_delay(
        self,
        notif_delay: str,
        notif_time_type: str,
        notif_time_has_HMS: bool,
    ) -> tuple[str, int]:
        # Need rework
        if notif_delay == "0":
            return " (now)", 0

        if notif_time_has_HMS:
            if notif_time_type == "S":
                return f" (in {notif_delay} seconds)", 1 * int(notif_delay)
            elif notif_time_type == "M":
                return f" (in {notif_delay} minutes)", 60 * int(notif_delay)
            elif notif_time_type == "H":
                return f" (in {notif_delay} hours)", 3600 * int(notif_delay)
        else:
            if notif_time_type == "D":
                return f" (in {notif_delay} days)", 86400 * int(notif_delay)
            elif notif_time_type == "W":
                return f" (in {notif_delay} weeks)", 604800 * int(notif_delay)
            elif notif_time_type == "M":
                return f" (in {notif_delay} months)", 2592000 * int(notif_delay)
        return f" (in {notif_delay} years)", 12 * 2592000 * int(notif_delay)

    def get_notif_date(
        self,
        notif_delay_secs: int,
        cal_event_date_strp: datetime,
        notif_delay_is_negative: bool,
    ) -> datetime:
        if notif_delay_is_negative:
            return cal_event_date_strp - timedelta(seconds=notif_delay_secs)
        return cal_event_date_strp + timedelta(seconds=notif_delay_secs)

    def correct_recurrent_date(
        self, notif_date_strp: datetime, event_recurrency: str
    ) -> datetime:
        while self.now_strp > notif_date_strp:
            if event_recurrency == "YEARLY":
                return notif_date_strp.replace(year=notif_date_strp.year + 1)
            elif event_recurrency == "MONTHLY":
                return notif_date_strp.replace(year=notif_date_strp.month + 1)
            elif event_recurrency == "WEEKLY":
                return notif_date_strp + timedelta(days=7)
            else:
                return notif_date_strp

    def check_if_notif_date_already_passed(
        self, notif_date_strp: datetime
    ) -> bool:
        if self.now_strp > notif_date_strp:
            return True
        return False

    def create_notif_entry(
        self,
        cal_file_uid: str,
        notif_date_strp: datetime,
        notif_msg: str,
        notif_msg_appendix: str,
    ) -> dict:
        return {
            "uid": cal_file_uid,
            "date": datetime.strftime(notif_date_strp, "%Y-%m-%d %H:%M"),
            "msg": notif_msg + notif_msg_appendix,
        }

    def schedule_notif(
        self, notifs: list, new_notif_entry: dict, new_notif_date_strp: datetime
    ) -> list:
        # need rework and variable renaming
        if len(notifs) == 0:
            notifs.append(new_notif_entry)
            return notifs

        for notif in notifs:
            notif_date = notif["date"]
            notif_date_strp = datetime.strptime(notif_date, "%Y-%m-%d %H:%M")
            if new_notif_date_strp <= notif_date_strp:
                notifs.insert(notifs.index(notif), new_notif_entry)
                return notifs
            elif new_notif_date_strp > notif_date_strp and notif == notifs[-1]:
                notifs.append(new_notif_entry)
                return notifs

    def refresh_notifs(self, notifs: list, cals_uids: list) -> list:
        """Assegura se algum cal_file foi apagado, eliminando as respectivas notifs
        N/A é para as notifs criadas manualmente fora de eventos de calendar"""

        return [
            notif
            for notif in notifs
            if notif["uid"] in cals_uids or notif["uid"] == "#N/A"
        ]
