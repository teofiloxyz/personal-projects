#!/usr/bin/python3
""" Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.
Também guarda o balanço, e é possível editá-lo."""

import os
import subprocess
import json
import sqlite3
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from Tfuncs import gmenu, oupt, fcol, ffmt


class Fintracker:
    def __init__(self):
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.now_strp = datetime.strptime(self.now, "%Y-%m-%d %H:%M:%S")
        self.message = list()

        with open("config.json", "r") as cf:
            self.json_info = json.load(cf)

        self.db_path = self.json_info["db_path"]

        if not os.path.isfile(self.db_path):
            self.setup_database()

        self.auto_transactions()

    def opening_message(self):
        if len(self.message) != 0:
            print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
            print("\n".join(self.message))
            print()

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        balance = (
            self.json_info["assets"].items(),
            self.json_info["liabilities"].items(),
        )
        for items in balance:
            for item, amount in items:
                if amount < 0:
                    need_to_edit_balance = True
                    print(
                        f"{ffmt.bold}{fcol.red}{item.capitalize()} "
                        f"is negative!{ffmt.reset}"
                    )

        if need_to_edit_balance:
            print(
                f"{ffmt.bold}{fcol.red}Please edit the balance "
                f"statement!{ffmt.reset}\n"
            )

        self.summary()


ft = Fintracker()
title = "Fintracker-Menu"
keys = {
    "ls": (
        lambda timespan=30: ft.show_transactions("all", timespan),
        "show past # (default 30) days transactions",
    ),
    "lse": (
        lambda timespan=30: ft.show_transactions("expenses", timespan),
        "show past # (default 30) days expenses",
    ),
    "lsr": (
        lambda timespan=30: ft.show_transactions("revenue", timespan),
        "show past # (default 30) days revenue",
    ),
    "lsb": (ft.show_balance, "show balance statement"),
    "sm": (ft.summary, "show summary"),
    "ad": (ft.add_transaction, "add transaction to database"),
    "rm": (ft.remove_transaction, "remove transaction from database"),
    "ed": (ft.edit_balance, "edit balance statement"),
    "ch": (ft.show_charts, "select and show charts"),
    "ex": (ft.export_to_csv, "export database tables to CSV file"),
}
extra_func = ft.opening_message
gmenu(title, keys, extra_func)
