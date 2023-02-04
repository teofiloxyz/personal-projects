#!/usr/bin/python3
# Script de notificações com diversas funções

from Tfuncs import Menu

import argparse

from scheduled import Scheduled, NotifSender
from history import History, UpdaterDaemon
from calendar_notifs import CalendarNotifs


class Notifications:
    def __init__(self) -> None:
        self.scheduled = Scheduled()
        self.history = History()

    def schedule_notif(self, message: str) -> None:
        self.scheduled.create_notif(message=" ".join(message), use_rofi=True)

    def start_history_daemon(self) -> None:
        UpdaterDaemon().start()

    def run_notif_sender(self) -> None:
        NotifSender().main()

    def run_calendar_notifs_scheduler(self) -> None:
        CalendarNotifs().main()

    def show_unseen_notifs(self) -> None:
        self.history.show_unseen_notifs(resend_notifs=True)

    def open_menu(self) -> None:
        menu = Menu(
            title="Notifications-Menu",
            beginning_func=self.history.show_unseen_notifs,
        )

        menu.add_option(
            key="ls",
            func=lambda days=15: self.scheduled.show(days_delta=int(days)),
            help="show scheduled notifications for the next # (default 15) days",
        )
        menu.add_option(
            key="lsh",
            func=lambda days=15: self.history.show(days_delta=int(days)),
            help="show past notifications of the last # (default 15) days",
        )
        menu.add_option(
            key="ad",
            func=self.scheduled.create_notif,
            help="schedule a notification",
        )
        menu.add_option(
            key="rm",
            func=self.scheduled.remove_notif,
            help="remove a scheduled notification",
        )
        menu.add_option(
            key="ed",
            func=self.scheduled.edit_notif,
            help="edit a scheduled notification",
        )

        menu.start()


def handle_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Notifications tool")
    ex_args = parser.add_mutually_exclusive_group()
    ex_args.add_argument(
        "-n",
        "--new-notif",
        help="schedule a new notification",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-d",
        "--history-daemon",
        help="initialize history updater daemon",
        action="store_true",
    )
    ex_args.add_argument(
        "-s",
        "--notif-sender",
        help="check if a scheduled notification is due",
        action="store_true",
    )
    ex_args.add_argument(
        "-c",
        "--calendar-notifs",
        help="auto-schedule calendar notifications",
        action="store_true",
    )
    ex_args.add_argument(
        "-u",
        "--show-unseen",
        help="show unseen notifications",
        action="store_true",
    )
    return parser.parse_args()


def main() -> None:
    notifs = Notifications()
    args = handle_cmd_args()

    funcs = {
        "new_notif": notifs.schedule_notif,
        "history_daemon": notifs.start_history_daemon,
        "notif_sender": notifs.run_notif_sender,
        "calendar_notifs": notifs.run_calendar_notifs_scheduler,
        "show_unseen": notifs.show_unseen_notifs,
    }

    # simplify this in the future
    for func in funcs:
        if getattr(args, func):
            command = func
            break
    else:
        command = None
    if not command:
        notifs.open_menu()
        return
    try:
        funcs[command](getattr(args, command))
    except TypeError:
        funcs[command]()


if __name__ == "__main__":
    main()
