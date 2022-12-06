#!/usr/bin/python3

from Tfuncs import ffmt, fcol

import os
import subprocess

from database import Database


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

    def choose_database(self) -> tuple[str, str] | str:
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
            return "q"

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
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        self.cursor.execute(f"pragma table_info({self.db_table})")
        columns = self.cursor.fetchall()
        entry = []

        db_tab_columns = Database.Query(db_path).get_columns(db_tab)

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

        # Tem que ser tuple
        entry = tuple(entry)
        self.cursor.execute(f"INSERT INTO {self.db_table} VALUES {entry}")
        self.db_con.commit()
        self.cursor.execute(
            f"SELECT * FROM {self.db_table} "
            f"WHERE rowid=(SELECT max(rowid) "
            f"FROM {self.db_table})"
        )

        last = self.cursor.fetchall()
        if last == [entry]:
            print(
                f"Entry added successfuly to '{self.db_table}' "
                f"from '{self.db_name}'"
            )
        else:
            print(
                "Error, something went wrong while adding the "
                "entry to the table"
            )

    def remove_entry_from_db_tab(self):
        db_name, db_path = self.choose_database()
        if db_path == "q":
            return

        db_tab = self.choose_database_tab(db_path)
        if db_tab == "q":
            return

        def get_int_rowid(rowid):
            try:
                rowid = int(rowid)
                if rowid not in self.df.index.tolist():
                    print("Number must be within the index range!")
                    return False
                return rowid
            except ValueError:
                print("Must be a number!")
                return False

        self.df_from_db_tab()
        print(
            f"{ffmt.bold}{fcol.green}{self.db_table.capitalize()} from "
            f"{self.db_name.capitalize()}:{ffmt.reset}\n{self.df_output}"
        )

        while True:
            rowid = input(
                "\nPick row id to remove or several " "(e.g.: 3+6+1+34): "
            )
            if rowid == "q":
                print("Aborted...")
                return
            elif "+" in rowid:
                rowid = rowid.split("+")
                rowid = [get_int_rowid(r) for r in rowid]
                if False not in rowid:
                    break
            else:
                rowid = get_int_rowid(rowid)
                if rowid is not False:
                    break

        self.df = self.df.drop(self.df.index[rowid])
        self.cursor.execute(f"DROP TABLE {self.db_table}")
        self.df.to_sql(self.db_table, self.db_con, index=False)
        self.refresh_dbs()

        db_tables_list = [
            x[1] for x in self.tabs_opts.values() if x[0] == self.db_path
        ]

        if self.db_table in db_tables_list:
            print("Entry removed!")
        else:
            print("Error, something went wrong replacing the table")

    def db_tab_to_csv(self):
        self.df_from_db_tab()
        csv_out = oupt.files(
            question="Enter the directory for the csv file: ",
            extension="csv",
            output_name=self.db_table,
        )
        if csv_out == "q":
            print("Aborted...")
            return

        self.df.to_csv(str(csv_out), encoding="utf-8", index=False)
        if os.path.exists(csv_out):
            print(f"Export done successfuly\nOutput at '{csv_out}'")
        else:
            print("Error, something went wrong exporting table to CSV")

    def csv_to_db_tab(self):
        db_tables_list = [
            x[1] for x in self.tabs_opts.values() if x[0] == self.db_path
        ]
        csv_in_path = inpt.files(
            question="Enter the CSV file to import: ", extensions="csv"
        )
        if csv_in_path == "q":
            print("Aborted...")
            return

        csv_in_name = os.path.basename(str(csv_in_path))
        new_db_table_name = os.path.splitext(csv_in_name)[0]
        while True:
            ans = input(
                f"Enter the name for the table, or leave empty to "
                f"name it '{new_db_table_name}': "
            )
            if ans == "q":
                print("Aborted...")
                return
            elif ans == "":
                break
            elif len(ans) < 30 and " " not in ans:
                if ans in db_tables_list:
                    print(f"There is already a table named '{ans}'")
                    continue
                else:
                    new_db_table_name = ans
                    break
            print("Invalid name, might be too big")

        self.df = pd.read_csv(str(csv_in_path), delimiter=",")
        self.df.to_sql(new_db_table_name, self.db_con, index=False)
        db_name = os.path.basename(self.db_path)
        self.refresh_dbs()
        db_tables_list = [
            x[1] for x in self.tabs_opts.values() if x[0] == self.db_path
        ]

        if new_db_table_name in db_tables_list:
            print(
                f"Import done successfuly\nTable '{new_db_table_name}' "
                f"created on '{db_name}'"
            )
        else:
            print("Error, something went wrong creating the table from CSV")

    def create_db_tab(self):
        db_tables_list = [
            x[1] for x in self.tabs_opts.values() if x[0] == self.db_path
        ]
        while True:
            db_table = input("Enter the name for the table: ")
            if db_table == "q":
                print("Aborted...")
                return
            elif len(db_table) < 30 and " " not in db_table:
                if db_table in db_tables_list:
                    print(f"There is already a table named '{db_table}'")
                    continue
                else:
                    break
            print("Invalid name, might be too big or has spaces")

        columns = ""
        columns_name_list = []
        columns_type_opts = {
            "0": "NULL",
            "1": "TEXT",
            "2": "INTEGER",
            "3": "REAL",
            "4": "BLOB",
        }
        while True:
            column_name = input(
                "Enter the name for a column, or leave empty "
                "to create the table: "
            )
            if column_name == "q":
                print("Aborted...")
                return
            elif column_name == "":
                if len(columns_name_list) == 0:
                    print("Cannot create a table without any column")
                    continue
                break
            elif column_name in columns_name_list:
                print("'{column_name}' is already on the list")
                continue
            elif len(column_name) > 30 or " " in column_name:
                print(
                    "Invalid name for a column, "
                    "might be too big or as spaces"
                )
                continue
            else:
                columns_type_opts_question = (
                    "\n".join(
                        sorted(
                            {f"[{x}] {y}" for x, y in columns_type_opts.items()}
                        )
                    )
                    + f"\nChoose the data_type for '{column_name}': "
                )
                column_type = qst.opts(
                    question=columns_type_opts_question,
                    opts_dict=columns_type_opts,
                )
                if column_type == "q":
                    print("Aborted...")
                    return
                columns_name_list.append((column_name, column_type))

        columns = ", ".join(f"{x[0]} {x[1]}" for x in columns_name_list)
        self.cursor.execute(f"CREATE TABLE {db_table} ({columns})")
        self.db_con.commit()
        self.refresh_dbs()
        db_tables_list = [
            x[1] for x in self.tabs_opts.values() if x[0] == self.db_path
        ]

        if db_table in db_tables_list:
            print(f"Table '{db_table}' created on '{self.db_name}'")
        else:
            print("Error, something went wrong creating the table")

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
