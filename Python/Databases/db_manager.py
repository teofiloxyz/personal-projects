import os
from typing import Optional

from database import Query as db_query, Edit as db_edit


class DBManager:
    def __init__(self) -> None:
        self.databases_dir = "databases_dir"

    def show_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        selected_db_name, selected_db_path = selected_db

        db_table = self._choose_database_table(selected_db_path)
        if not db_table:
            print("Aborted...")
            return

        print(f"{db_table.capitalize()} from {selected_db_name.capitalize()}:")
        df = db_query(selected_db_path).create_df(db_table)
        print(df)

    def add_entry_to_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        _, selected_db_path = selected_db

        db_table = self._choose_database_table(selected_db_path)
        if not db_table:
            print("Aborted...")
            return

        columns = db_query(selected_db_path).get_table_columns(db_table)
        entry = self._get_entry_for_table(columns)
        if not entry:
            print("Aborted...")
            return
        db_edit(selected_db_path).add_entry(db_table, entry)

    def _get_entry_for_table(self, table_columns: list) -> Optional[tuple]:
        entry = []
        for column in table_columns:
            column_name = column[1]
            column_type = column[2]
            column_entry = input(
                f"Enter the entry for {column_name} ({column_type}): "
            )

            try:
                if column_type == "INTEGER":
                    column_entry = int(column_entry)
                elif column_type == "REAL":
                    column_entry = float(column_entry)
                entry.append(column_entry)
            except ValueError:
                print(f"Invalid input for {column_name}...")
                return None
        return tuple(entry)

    def remove_entry_from_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        selected_db_name, selected_db_path = selected_db

        db_table = self._choose_database_table(selected_db_path)
        if not db_table:
            print("Aborted...")
            return

        print(f"{db_table.capitalize()} from {selected_db_name.capitalize()}:")
        df = db_query(selected_db_path).create_df(db_table)
        print(df)

        row_ids = self._get_valid_row_ids(df)
        if row_ids:
            [
                db_edit(selected_db_path).remove_entry(db_table, row_id)
                for row_id in row_ids
            ]
        else:
            print("Aborted...")

    def _get_valid_row_ids(self, df) -> Optional[list[int]]:
        prompt = input("\nPick row id to remove or several (e.g.: 3+6+1+34): ")
        if prompt == "q":
            return None

        row_ids = prompt.split("+")
        try:
            row_ids = [int(row_id) for row_id in row_ids]
        except ValueError:
            print("Must be a number!")
            return None

        if not all(row_id in df.index.tolist() for row_id in row_ids):
            print("Number must be within the index range!")
            return None
        return row_ids

    def db_table_to_csv(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        _, selected_db_path = selected_db

        db_table = self._choose_database_table(selected_db_path)
        if not db_table:
            print("Aborted...")
            return

        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return

        df = db_query(selected_db_path).create_df(db_table)
        df.to_csv(csv_output, encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")

    def csv_to_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        _, selected_db_path = selected_db

        db_table_names = self._get_database_table_names(selected_db_path)
        if len(db_table_names) == 0:
            print("Aborted...")
            return

        csv_input = input("Enter csv input path: ")
        if csv_input == "q":
            print("Aborted...")
            return

        csv_name = os.path.basename(csv_input)
        db_table_name = os.path.splitext(csv_name)[0]
        db_table_name = self._get_db_table_name(db_table_names, db_table_name)
        if not db_table_name:
            print("Aborted...")
            return

        db_edit(selected_db_path).create_table_from_csv(
            csv_input, db_table_name
        )

    def _get_db_table_name(
        self, db_table_names: list[str], db_table_name: Optional[str] = None
    ) -> Optional[str]:
        if db_table_name:
            prompt = input(
                f"Enter the name for the table, or leave empty to "
                f"name it '{db_table_name}': "
            )
            if prompt == "":
                prompt = db_table_name
        else:
            prompt = input("Enter the name for the table: ")

        if prompt == "q":
            return None
        elif len(prompt) > 40 or " " in prompt:
            print("Invalid name, might be too big or has spaces...")
            return None

        if db_table_name in db_table_names:
            print(f"There is already a table named '{prompt}'")
            return None
        return prompt

    def create_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        _, selected_db_path = selected_db

        db_table_names = self._get_database_table_names(selected_db_path)
        db_table_name = self._get_db_table_name(db_table_names)
        if not db_table_name:
            print("Aborted...")
            return

        column_names = self._get_column_names()
        if not column_names:
            print("Aborted...")
            return
        column_types = self._get_column_types(column_names)
        if not column_types:
            print("Aborted...")
            return
        columns = ", ".join(
            f"{col_name} {col_type}"
            for col_name, col_type in zip(column_names, column_types)
        )

        db_edit(selected_db_path).create_table(db_table_name, columns)

    def _get_column_names(self) -> Optional[list[str]]:
        column_names = []
        while True:
            prompt = input(
                "Enter the name for a column, or leave empty "
                "to create the table: "
            )
            if prompt == "q":
                return None
            elif prompt == "":
                if len(column_names) == 0:
                    print("Cannot create a table without any column...")
                    continue
                break
            elif prompt in column_names:
                print(f"'{prompt}' is already a column...")
                continue
            elif len(prompt) > 40 or " " in prompt:
                print("Name might be too big or as spaces...")
                continue
            column_names.append(prompt)
        return column_names

    def _get_column_types(self, column_names: list[str]) -> Optional[list[str]]:
        column_types = []
        column_type_opts = {
            "0": "NULL",
            "1": "TEXT",
            "2": "INTEGER",
            "3": "REAL",
            "4": "BLOB",
        }
        for column in column_names:
            print(column_type_opts)
            prompt = input(f"\nChoose the data_type for '{column}': ")
            if prompt not in column_type_opts.keys():
                return None
            column_types.append(column_type_opts[prompt])

    def remove_db_table(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        selected_db_name, selected_db_path = selected_db

        db_table = self._choose_database_table(selected_db_path)
        if not db_table:
            print("Aborted...")
            return

        prompt = input(
            f":: Are you sure you want to remove '{db_table}' "
            f"from '{selected_db_name}' [y/N] "
        )
        if prompt.lower() == "y":
            db_edit(selected_db_path).remove_table(db_table)

    def create_db(self) -> None:
        databases = self._get_databases()
        new_db = input("Enter the name for the new database: ")
        if new_db == "q":
            print("Aborted...")
            return
        if not new_db.endswith(".db"):
            new_db += ".db"

        new_selected_db_path = os.path.join(self.databases_dir, new_db)
        if new_selected_db_path in databases:
            print(f"{new_db} already exists\nAborted...")
            return

        open(new_selected_db_path, "x")
        if os.path.isfile(new_selected_db_path):
            print(f"Database created successfuly at '{new_selected_db_path}'")
        else:
            print("Error, something went wrong while creating the database")

    def remove_db(self) -> None:
        selected_db = self._choose_database()
        if not selected_db:
            print("Aborted...")
            return
        selected_db_name, selected_db_path = selected_db

        prompt = input(
            f":: Are you sure you want to remove '{selected_db_name}' [y/N] "
        )
        if prompt.lower() == "y":
            os.remove(selected_db_path)
            print("Database removed!")

    def _get_databases(self) -> list[str]:
        return [
            os.path.join(self.databases_dir, database)
            for database in os.listdir(self.databases_dir)
            if database.endswith(".db")
        ]

    def _get_database_table_names(self, selected_db_path: str) -> list[str]:
        return db_query(selected_db_path).get_tables()

    def _choose_database(self) -> Optional[tuple[str, str]]:
        databases = self._get_databases()
        [
            print(f"[{n}] {os.path.basename(selected_db_path)}")
            for n, selected_db_path in enumerate(databases, 1)
        ]
        prompt = input("Pick one database: ")
        try:
            selected_db_path = databases[int(prompt) - 1]
        except (IndexError, ValueError):
            return None

        selected_db_name = os.path.basename(selected_db_path)
        return selected_db_name, selected_db_path

    def _choose_database_table(self, selected_db_path: str) -> Optional[str]:
        db_table_names = self._get_database_table_names(selected_db_path)
        if len(db_table_names) == 0:
            print("This database has no tables...")
            return None
        elif len(db_table_names) == 1:
            db_table = db_table_names[0]
            print(f"This database has 1 table: {db_table}")
            return db_table

        [
            print(f"[{n}] {db_table}")
            for n, db_table in enumerate(db_table_names, 1)
        ]
        prompt = input("Pick one table: ")
        try:
            db_table = db_table_names[int(prompt) - 1]
        except (IndexError, ValueError):
            return None

        return db_table
