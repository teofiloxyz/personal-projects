#!/usr/bin/python3


class History:
    def history_append(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "cmd_input" in self.__dict__:
            entry = f"{self.hkey}{self.cmd_input}".replace(",", "")
        else:
            entry = str(self.hkey).replace(",", "")

        with open(self.history_path, "a") as hs:
            hs.write(f"{now},{entry}\n")

    def history_menu(self):
        import pandas as pd

        df = pd.read_csv(self.history_path)
        # Dataframe apenas com as hkeys (sem rkeys ou inputs)
        df = df[df.entry.isin(self.hkeys)]
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
