#!/usr/bin/python3

from database import Database


class CSVFile:
    def export_csv(self, db_path: str, db_table: str) -> None:
        # df = pd.read_sql(
        #    "SELECT * FROM transactions LEFT JOIN expenses "
        #    "USING(transaction_id)",
        #    self.db_con,
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return

        df = Database.Query(db_path).create_df(db_table)
        df.to_csv(str(csv_output), encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")
