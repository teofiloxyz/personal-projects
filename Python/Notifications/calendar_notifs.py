"""Deve ser usado após a criação/edição de eventos no calendário,
de modo a criar notificações no ficheiro de scheduled."""

import os

from utils import Utils, Notif


class CalendarNotifs:
    utils = Utils()
    cals_path = "calendars_path"
    last_update_path = "last_calendar_update"
    notifs = utils.get_scheduled_notifs()

    def main(self) -> None:
        last_update = self.get_last_update()
        last_update_strp = self.utils.get_date_strp(last_update)

        notifs_uids = self.get_notifs_uids()
        cals_uids = list()

        cal_files = self.get_cal_files()
        for cal_file in cal_files:
            cal_file_uid = self.get_cal_file_uid(cal_file)
            cals_uids.append(cal_file_uid)

            is_rec_and_already_scheduled = (
                self.check_if_rec_and_already_scheduled(
                    cal_file, cal_file_uid, notifs_uids
                )
            )
            cal_file_modif_date = self.utils.get_file_modif_date(cal_file)
            cal_file_modif_date_strp = self.utils.get_date_strp(
                cal_file_modif_date
            )
            is_new = self.utils.check_if_date_a_is_newer(
                cal_file_modif_date_strp, last_update_strp
            )
            if is_rec_and_already_scheduled or not is_new:
                continue

            if cal_file_uid in notifs_uids:
                # Acaba por ser modificado, ao apagar e criar nova(s)
                self.delete_event_notifs(cal_file_uid)

            cal_file_lines = self.get_cal_file_lines(cal_file)
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
            cal_event_date_strp = self.utils.get_date_strp(
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
                    notif_date_strp = self.utils.get_date_with_delay(
                        cal_event_date_strp,
                        notif_delay_secs,
                        notif_delay_is_negative,
                    )
                else:
                    notif_date_strp = self.utils.get_date_with_delay(
                        cal_event_date_strp,
                        notif_delay_secs,
                        notif_delay_is_negative,
                    )
                    notif_msg_appendix = ""

                if event_is_recurrent:
                    notif_date_strp = (
                        self.utils.correct_recurrent_calendar_date(
                            notif_date_strp, event_recurrency
                        )
                    )

                if self.utils.check_if_date_is_due(notif_date_strp):
                    continue

                notifs_uids.append(cal_file_uid)

                date, hour = self.utils.get_date_strf(notif_date_strp).split()
                notif = Notif(
                    uid=cal_file_uid,
                    date=date,
                    hour=hour,
                    title="Calendar",
                    message=notif_msg + notif_msg_appendix,
                )
                self.notifs.append(notif)
                self.notifs = sorted(
                    self.notifs, key=lambda notif: (notif.date + notif.hour)
                )

        self.refresh_notifs(cals_uids)
        self.utils.save_scheduled_notifs(self.notifs)
        self.refresh_last_update()

    def get_last_update(self) -> str:
        if not os.path.isfile(self.last_update_path):
            return "2000-01-01 00:00:01"
        with open(self.last_update_path, "r") as f:
            return f.readline()

    def get_notifs_uids(self) -> list:
        return [notif.uid for notif in self.notifs]

    def get_cal_files(self) -> list[str]:
        return [
            os.path.join(root_dirs_files[0], file)
            for root_dirs_files in os.walk(self.cals_path)
            for file in root_dirs_files[2]
        ]

    def get_cal_file_uid(self, cal_file: str) -> str:
        return os.path.basename(cal_file).split(".")[0]

    def check_if_rec_and_already_scheduled(
        self, cal_file: str, cal_file_uid: str, notifs_uids: list[str]
    ) -> bool:
        """Para os calendários recurrentes: Caso o evento já tenha passado
        e o ficheiro não seja recente, volta a criar um novo evento para
        a próxima data, de acordo com a respetiva recurrência"""

        if "personal" not in cal_file and cal_file_uid in notifs_uids:
            return True
        return False

    def delete_event_notifs(self, cal_file_uid: str) -> None:
        """Plural because one cal event can have several scheduled notifs"""
        self.notifs = [
            notif for notif in self.notifs if notif.uid != cal_file_uid
        ]

    def get_cal_file_lines(self, cal_file: str) -> list[str]:
        with open(cal_file, "r") as cf:
            return cf.readlines()

    def get_cal_file_info(
        self, cal_file: str, cal_file_lines: list[str]
    ) -> tuple:
        # Needs rework
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
                if "FREQ=YEARLY" in line:
                    event_recurrency = "YEARLY"
                elif "FREQ=MONTHLY" in line:
                    event_recurrency = "MONTHLY"
                else:
                    event_recurrency = "WEEKLY"

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
        # Needs rework
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

    def refresh_notifs(self, cals_uids: list) -> None:
        """Assegura se algum cal_file foi apagado, eliminando
        as respectivas notifs; uid == "" é para as notifs criadas
        manualmente fora de eventos de calendar"""

        self.notifs = [
            notif
            for notif in self.notifs
            if notif.uid in cals_uids or notif.uid == ""
        ]

    def refresh_last_update(self) -> None:
        with open(self.last_update_path, "w") as f:
            f.write(self.utils.get_date_now())
