#!/usr/bin/python3


class Databases:
    def __init__(self):
        self.databases_path = "databases_path"

    def refresh_dbs(self):
        (
            self.dbs_opts,
            self.tabs_opts,
            self.dbs_opts_info,
            self.tabs_opts_info,
            n_db,
            n_tab,
        ) = ({}, {}, "", "", 1, 1)

        for root_dirs_files in os.walk(self.databases_path):
            for file in root_dirs_files[2]:

                if file.endswith(".db"):
                    db_path = os.path.join(root_dirs_files[0], file)
                    db_name = os.path.basename(db_path)
                    self.dbs_opts[str(n_db)] = db_path
                    self.dbs_opts_info += f"[{n_db}]: {db_name}\n"
                    n_db += 1
                    tables = str(
                        subprocess.run(
                            ["sqlite3", db_path, ".tables"],
                            stdout=subprocess.PIPE,
                        ).stdout
                    )[2:-3]

                    if " " in tables:
                        tables = tables.split()
                        for table in tables:
                            self.tabs_opts[str(n_tab)] = (db_path, table)
                            self.tabs_opts_info += (
                                f"[{n_tab}]: {table} " f"from {db_name}\n"
                            )
                            n_tab += 1
                    else:
                        self.tabs_opts[str(n_tab)] = (db_path, tables)
                        self.tabs_opts_info += (
                            f"[{n_tab}]: {tables} " f"from {db_name}\n"
                        )
                        n_tab += 1

    def choose_db(self):
        self.db_path = qst.opts(
            question=f"{self.dbs_opts_info}q: quit to "
            f"main menu\n\n{ffmt.bold}{fcol.yellow}"
            f"Choose the database: {ffmt.reset}",
            opts_dict=self.dbs_opts,
        )
        if self.db_path == "q":
            print("Aborted...")
            return False

        self.db_name = os.path.basename(self.db_path)

    def choose_db_tab(self):
        tab = qst.opts(
            question=f"{self.tabs_opts_info}q: quit to main "
            f"menu\n\n{ffmt.bold}{fcol.yellow}Choose the table: "
            f"{ffmt.reset}",
            opts_dict=self.tabs_opts,
        )
        if tab == "q":
            print("Aborted...")
            return False

        self.db_path = tab[0]
        self.db_table = tab[1]
        self.db_name = os.path.basename(self.db_path)

    def connect_to_db(self):
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()

    def disconnect_from_db(self):
        self.db_con.close()

    def df_from_db_tab(self):
        self.df = pd.read_sql(f"SELECT * FROM {self.db_table}", self.db_con)
        self.df_output = self.df.to_string()

    @staticmethod
    def generic_connection(show_only_dbs=False):
        def decorator(func):
            def process(self):
                self.refresh_dbs()

                if show_only_dbs is False:
                    if self.choose_db_tab() is False:
                        return
                else:
                    if self.choose_db() is False:
                        return

                self.connect_to_db()
                func(self)
                self.disconnect_from_db()

            return process

        return decorator
