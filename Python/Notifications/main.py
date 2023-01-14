#!/usr/bin/python3
# Script de notificações com diversas funções

from Tfuncs import gmenu

import argparse

from scheduled import Scheduled, NotifSender
from history import History
from calendar_notifs import CalendarNotifs


def main() -> None:
    new_notif, hist_daemon, notif_listener, calendar_notif, show_unseen = cmd()
    if new_notif is not None:
        Scheduled().create_notif(message=" ".join(new_notif), use_rofi=True)
    elif hist_daemon:
        History().start_updater_daemon()
    elif notif_listener:
        NotifSender().main()
    elif calendar_notif:
        CalendarNotifs().main()
    elif show_unseen:
        History().show_unseen_notifs(resend_notifs=True)
    else:
        open_menu()


def cmd() -> tuple:
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
        "--hist-daemon",
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
        "--calendar-notif",
        help="auto-schedule calendar notifications",
        action="store_true",
    )
    ex_args.add_argument(
        "-u",
        "--show-unseen",
        help="show unseen notifications",
        action="store_true",
    )
    args = parser.parse_args()
    return (
        args.new_notif,
        args.hist_daemon,
        args.notif_sender,
        args.calendar_notif,
        args.show_unseen,
    )


def open_menu() -> None:
    hist = History()
    schd = Scheduled()
    title = "Notifications-Menu"
    keys = {
        "ls": (
            lambda days=30: schd.show(days_limit=int(days)),
            "show scheduled notifications for the next # (default 30) days",
        ),
        "lsh": (hist.show_all, "show all past notifications"),
        "ad": (schd.create_notif, "schedule a notification"),
        "rm": (schd.remove_notif, "remove a scheduled notification"),
        "ed": (schd.edit_notif, "edit a scheduled notification"),
    }
    extra_func = hist.show_unseen_notifs
    gmenu(title, keys, extra_func)


if __name__ == "__main__":
    main()
