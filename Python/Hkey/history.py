#!/usr/bin/python3

from datetime import datetime

HIST_PATH = "hist_path"


class History:
    @staticmethod
    def history_append(hkey: str, cmd_input: str = "") -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "cmd_input" != "":
            entry = f"{hkey}{cmd_input}".replace(",", "")
        else:
            entry = hkey.replace(",", "")

        with open(HIST_PATH, "a") as hs:
            hs.write(f"{now},{entry}\n")

    @staticmethod
    def history_menu() -> None:
        import pandas as pd

        df = pd.read_csv(HIST_PATH)
        options = {
            "top": lambda num: print(
                df["entry"].value_counts()[: int(num)] / len(df.index) * 100
            ),
            "bot": lambda num: print(
                (
                    df["entry"].value_counts()[-int(num) :]
                    / len(df.index)
                    * 100
                ).iloc[::-1]
            ),
        }
        help_dialog = " <top x>: top x\n <bot x>: bot x\n"

        print("History Menu")
        while True:
            entry = input("Search entry: ")
            if entry == "q":
                print("Exited History Menu")
                return
            elif entry[:3] in options:
                options[entry[:3]](entry[4:])
            else:
                print(help_dialog)
