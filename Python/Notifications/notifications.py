#!/usr/bin/python3
# Script de notificações com diversas funções
# Whole script still needs work

from Tfuncs import gmenu

import argparse

from scheduled import Scheduled
from history import History
from notifs_listener import NotifsListener
from calendar_notifs import CalendarNotifs


def main() -> None:
    new_notif, update_hist, notif_listener, calendar_notif = cmd()
    if new_notif is not None:
        Scheduled().create_notif(msg=" ".join(new_notif))
    elif update_hist:
        History().update_hist()
    elif notif_listener:
        NotifsListener().main()
    elif calendar_notif:
        CalendarNotifs().main()
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
        "-u",
        "--update-hist",
        help="update notifications history",
        action="store_true",
    )
    ex_args.add_argument(
        "-l",
        "--notif-listener",
        help="check if a scheduled notification is due",
        action="store_true",
    )
    ex_args.add_argument(
        "-c",
        "--calendar-notif",
        help="auto-schedule calendar notifications",
        action="store_true",
    )
    args = parser.parse_args()
    return (
        args.new_notif,
        args.update_hist,
        args.notif_listener,
        args.calendar_notif,
    )


def open_menu() -> None:
    hist = History()
    schd = Scheduled()
    title = "Notifications-Menu"
    keys = {
        "ls": (
            lambda days=30: schd.show(days=days),
            "show scheduled notifications for the next # (default 30) days",
        ),
        "lsh": (hist.show_all, "show all past notifications"),
        "lsl": (
            lambda: hist.show_all_filter_urg("low"),
            "show all low urgency past notifications",
        ),
        "lsn": (
            lambda: hist.show_all_filter_urg("normal"),
            "show all normal urgency past notifications",
        ),
        "lsc": (
            lambda: hist.show_all_filter_urg("critical"),
            "show all critical urgency past notifications",
        ),
        "ad": (schd.create_notif, "schedule a notification"),
        "rm": (schd.remove_notif, "remove a scheduled notification"),
    }
    extra_func = hist.show_unseen_notifs
    gmenu(title, keys, extra_func)


if __name__ == "__main__":
    main()
