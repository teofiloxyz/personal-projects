from database import Database


class CSVFile:
    @staticmethod
    def export_csv() -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return

        df = Database().Query().create_df_with_transactions()
        df.to_csv(str(csv_output), encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")
