from Tfuncs import inpt, oupt

from database import Database
from playlist import Playlist


class CSVFile:
    def choose_playlist(self, operation: str) -> None:
        playlist = input(f"Choose [p]laylist or [a]rchive to {operation}: ")
        if playlist == "p":
            self.playlist = "playlist"
        elif playlist == "a":
            self.playlist = "archive"
        else:
            print("Aborted...")
            return

    def import_csv(self) -> None:
        self.choose_playlist(operation="import")
        csv_input = inpt.files("Enter csv input path: ", extensions="csv")
        if csv_input == "q":
            print("Aborted...")
            return
        with open(csv_input, "r") as cs:
            lines = cs.readlines()
        header = "date_added,title,ytb_code,genre"
        if lines[0].strip("\n") != header:
            print(f'"Csv header must be: "{header}"')
            return

        Database().reset_table(self.playlist)

        for line in lines[1:]:
            entry = tuple(line.strip("\n").split(","))
            Playlist(self.playlist).add(entry)
        print("Import complete!")

    def export_csv(self) -> None:
        self.choose_playlist(operation="export")
        csv_output = oupt.files(
            question="Enter csv output path: ",
            extension="csv",
            output_name=f"music_{self.playlist}",
        )
        if csv_output == "q":
            print("Aborted...")
            return

        df_cols = "date_added, title, ytb_code, genre"
        df = Database().Query().create_df(self.playlist, selection=df_cols)
        df.to_csv(str(csv_output), encoding="utf-8", index=False)
        print(f"Export done\nOutput at '{csv_output}'")
