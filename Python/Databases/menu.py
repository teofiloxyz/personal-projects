from Tfuncs import ffmt, fcol

import os
import subprocess

from database import Database
from csvfile import CSVFile


class Menu:
    def __init__(self) -> None:
        self.databases_dir = "databases_dir"

    def get_databases(self) -> list[str]:
        return [
            os.path.join(self.databases_dir, database)
            for database in os.listdir(self.databases_dir)
            if database.endswith(".db")
        ]

    def get_database_tabs(self, db_path: str) -> list[str]:
        return Database.Query(db_path).get_tabs()

    def choose_database(self) -> tuple[str, str]:
        databases = self.get_databases()
        [
            print(f"[{n}] {os.path.basename(db_path)}")
            for n, db_path in enumerate(databases, 1)
        ]
        prompt = input("Pick one database: ")
        try:
            db_path = databases[int(prompt) - 1]
        except (IndexError, ValueError):
            print("Aborting...")
            return ("q", "q")

        db_name = os.path.basename(db_path)
        return db_name, db_path

    def choose_database_tab(self, db_path: str) -> str:
        db_tabs = self.get_database_tabs(db_path)
        if len(db_tabs) == 0:
            print("This database has no tables...")
            print("Aborting...")
            return "q"
        elif len(db_tabs) == 1:
            db_tab = db_tabs[0]
            print(f"This database has 1 table: {db_tab}")
            return db_tab

        [print(f"[{n}] {db_tab}") for n, db_tab in enumerate(db_tabs, 1)]
        prompt = input("Pick one table: ")
        try:
            db_tab = db_tabs[int(prompt) - 1]
        except (IndexError, ValueError):
            print("Aborting...")
            return "q"

        return db_tab

    def show_db_tab(self) -> None:
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        print(
            f"{ffmt.bold}{fcol.green}{db_tab.capitalize()} from "
            f"{db_name.capitalize()}:{ffmt.reset}"
        )
        df = Database.Query(db_path).create_df(db_tab)
        print(df)

    def add_entry_to_db_tab(self) -> None:
        _, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        columns = Database.Query(db_path).get_tab_columns(db_tab)
        entry = []
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            column_entry = input(
                f"Enter the entry for " f"{column_name} ({column_type}): "
            )

            if column_type == "INTEGER":
                column_entry = int(column_entry)
            elif column_type == "REAL":
                column_entry = float(column_entry)
            entry.append(column_entry)

        Database.Edit(db_path).add_entry(db_tab, tuple(entry))

    def remove_entry_from_db_tab(self) -> None:
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        print(
            f"{ffmt.bold}{fcol.green}{db_tab.capitalize()} from "
            f"{db_name.capitalize()}:{ffmt.reset}"
        )
        df = Database.Query(db_path).create_df(db_tab)
        print(df)

        while True:
            prompt = input(
                "\nPick row id to remove one or several (e.g.: 3+6+1+34): "
            )
            if prompt == "q":
                print("Aborted...")
                return
            elif "+" in prompt:
                rowids = prompt.split("+")
            else:
                rowids = list(prompt)

            try:
                [int(rowid) for rowid in rowids]
            except ValueError:
                print("Must be a number!")
                continue

            df_index = df.index.tolist()
            for rowid in rowids:
                if rowid not in df_index:
                    print("Number must be within the index range!")
                    continue
            break

        [Database.Edit(db_path).remove_entry(db_tab, rowid) for rowid in rowids]

    def db_tab_to_csv(self) -> None:
        _, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return

        df = Database.Query(db_path).create_df(db_table)
        df.to_csv(str(csv_output), encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")

    def csv_to_db_tab(self) -> None:
        _, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tabs = self.get_database_tabs(db_path)

        csv_input = input("Enter csv input path: ")
        if csv_input == "q":
            print("Aborted...")
            return

        csv_name = os.path.basename(csv_input)
        db_tab_name = os.path.splitext(csv_name)[0]

        while True:
            prompt = input(
                f"Enter the name for the table, or leave empty to "
                f"name it '{db_tab_name}': "
            )
            if prompt == "q":
                print("Aborted...")
                return
            elif prompt == "":
                break
            elif len(prompt) > 30 or " " in prompt:
                print("Invalid name, might be too big")
                continue

            if prompt in db_tabs:
                print(f"There is already a table named '{prompt}'")
                continue
            else:
                break

        db_tab_name = prompt
        Database.Edit(db_path).create_tab_from_csv(csv_input, db_tab_name)

    def create_db_tab(self) -> None:
        _, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tabs = self.get_database_tabs(db_path)

        while True:
            prompt = input("Enter the name for the table: ")
            if prompt == "q":
                print("Aborted...")
                return
            elif len(prompt) > 30 or " " in prompt:
                print("Invalid name, might be too big or has spaces")
                continue

            if prompt in db_tabs:
                print(f"There is already a table named '{prompt}'")
                continue
            else:
                break
        db_tab = prompt

        columns_name_list = []
        columns_type_opts = {
            "0": "NULL",
            "1": "TEXT",
            "2": "INTEGER",
            "3": "REAL",
            "4": "BLOB",
        }
        while True:
            prompt = input(
                "Enter the name for a column, or leave empty "
                "to create the table: "
            )
            if prompt == "q":
                print("Aborted...")
                return
            elif prompt == "":
                if len(columns_name_list) == 0:
                    print("Cannot create a table without any column")
                    continue
                break
            elif prompt in columns_name_list:
                print(f"'{prompt}' is already a column")
                continue
            elif len(prompt) > 30 or " " in prompt:
                print(
                    "Invalid name for a column, "
                    "might be too big or as spaces"
                )
                continue
            else:
                column_name = prompt
                col_type_qst = (
                    "\n".join(
                        sorted(
                            {f"[{x}] {y}" for x, y in columns_type_opts.items()}
                        )
                    )
                    + f"\nChoose the data_type for '{column_name}': "
                )
                prompt = input(col_type_qst)
                if prompt == "q":
                    print("Aborted...")
                    return
                column_type = prompt
                columns_name_list.append((column_name, column_type))

        columns = ", ".join(f"{x[0]} {x[1]}" for x in columns_name_list)
        Database.Edit(db_path).create_tab(db_tab, columns)

    def remove_db_tab(self) -> None:
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        if (
            input(
                f":: Are you sure you want to remove '{db_tab}' "
                f"from '{db_name}' [y/N] "
            )
            == "y"
        ):
            Database.Edit(db_path).remove_tab(db_tab)

    def create_db(self) -> None:
        databases = self.get_databases()
        while True:
            new_db = input("Enter the name for the new database: ")
            if new_db == "q":
                print("Aborting...")
                return
            elif "/" in new_db or " " in new_db or len(new_db) > 30:
                print("Invalid name for a database")
                continue
            if not new_db.endswith(".db"):
                new_db += ".db"
            new_db_path = os.path.join(self.databases_dir, new_db)
            if new_db_path in databases:
                print(f"{new_db} already exists")
                continue
            break

        subprocess.run(["touch", new_db_path])
        if os.path.exists(new_db_path):
            print(f"Database created successfuly at '{new_db_path}'")
        else:
            print("Error, something went wrong while creating the database")

    def remove_db(self) -> None:
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        if (
            input(f":: Are you sure you want to remove '{db_name}' [y/N] ")
            == "y"
        ):
            os.remove(db_path)
            print("Database removed!")
