#!/usr/bin/python3
# Menu de notificações com diversas funções

import os
import sys
import pickle
from datetime import datetime, timedelta
from Tfuncs import gmenu, ffmt, fcol, qst, rofi


def show_new_notif():
    config = ConfigParser()
    config.read("config.ini")
    new_notif_path = config["HISTORY"]["new_path"]
    if not os.path.exists(new_notif_path):
        print("No new notifications...")
        return

    print(f"{ffmt.bold}{fcol.red}NEW:{ffmt.reset}")
    notif_list = get_notif_list(new_notif_path)

    print(
        *(f'{notif["time"]} - {notif["message"]}' for notif in notif_list),
        sep="\n",
    )
    os.remove(new_notif_path)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        msg = " ".join(sys.argv[2:])
        if sys.argv[1] == "create_notif":
            Scheduled().create_alarm(msg, use_rofi=True)
        else:
            print("Argument error...")
    else:
        hist = History()
        schd = Scheduled()
        title = "Notifications-Menu"
        keys = {
            "ls": (
                lambda days=30: schd.show_scheduled_alarms(days=days),
                "show scheduled alarms for next # (default 30) days",
            ),
            "lsh": (hist.show_all, "show all past notifications"),
            "lsl": (
                lambda: hist.show_filter_urg("low"),
                "show all low urgency past notifications",
            ),
            "lsn": (
                lambda: hist.show_filter_urg("normal"),
                "show all normal urgency past notifications",
            ),
            "lsc": (
                lambda: hist.show_filter_urg("critical"),
                "show all critical urgency past notifications",
            ),
            "ad": (schd.create_alarm, "create a notification alarm"),
            "rm": (schd.remove_alarm, "remove a scheduled notification alarm"),
        }
        extra_func = show_new_notif
        gmenu(title, keys, extra_func)
