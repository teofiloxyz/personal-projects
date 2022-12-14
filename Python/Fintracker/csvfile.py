#!/usr/bin/python3


class CSVFile:
    def export_to_csv(self):
        df = pd.read_sql(
            "SELECT * FROM transactions LEFT JOIN expenses "
            "USING(transaction_id)",
            self.db_con,
        )

        csv_out = oupt.files(
            question="Enter the path to save the csv file: ",
            extension="csv",
            output_name="fintracker_table",
        )
        if csv_out == "q":
            print("Aborted...")
            return

        df.to_csv(str(csv_out), encoding="utf-8", index=False)

        if os.path.exists(csv_out):
            print(f"Export done successfuly\nOutput at '{csv_out}'")
        else:
            print("Error, something went wrong exporting to CSV")
