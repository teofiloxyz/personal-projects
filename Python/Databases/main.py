#!/usr/bin/python3

import os
import sqlite3
import subprocess
import pandas as pd
from Tfuncs import gmenu, ffmt, fcol, qst, inpt, oupt


db = Databases()
title = "Databases-Menu"
keys = {
    "ls": (db.show_db_tab, "show database table"),
    "ad": (db.add_entry_to_db_tab, "add entry to a database table"),
    "rm": (db.remove_entry_from_db_tab, "remove entry from database table"),
    "dc": (db.db_tab_to_csv, "export database table to csv"),
    "cd": (db.csv_to_db_tab, "import database table from csv"),
    "adt": (db.create_db_tab, "create new database table"),
    "rmt": (db.remove_db_tab, "remove database table"),
    "add": (db.create_db, "create new database"),
    "rmd": (db.remove_db, "remove database"),
}
gmenu(title, keys)
