#!/usr/bin/python3

import os

from database import Database


class CSVFile:
    def import_csv(self, db_path: str, db_tabs: list[str]) -> None:
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

    def export_csv(self, db_path: str, db_table: str) -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return

        df = Database.Query(db_path).create_df(db_table)
        df.to_csv(str(csv_output), encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")
