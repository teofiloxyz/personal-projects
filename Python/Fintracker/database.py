#!/usr/bin/python3


class Database:
    self.db_path = self.json_info["db_path"]

    if not os.path.isfile(self.db_path):
        self.setup_database()

    self.auto_transactions()

    def setup_database(self):
        subprocess.run(["touch", self.db_path])

        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()

        self.cursor.execute(
            "CREATE TABLE transactions(transaction_id "
            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "
            "UNIQUE, time TEXT NOT NULL, trn_type TEXT "
            "NOT NULL, amount REAL NOT NULL, note TEXT)"
        )
        # Eu sei que podia ficar tudo numa tabela com category NULL
        self.cursor.execute(
            "CREATE TABLE expenses(transaction_id "
            "INTEGER, category TEXT NOT NULL, "
            "FOREIGN KEY(transaction_id) "
            "REFERENCES transactions(transaction_id))"
        )
        self.db_con.commit()

        self.db_con.close()

    def generic_connection(func):
        def process(self, *args, **kwargs):
            self.db_con = sqlite3.connect(self.db_path)
            self.cursor = self.db_con.cursor()
            func(self, *args, **kwargs)
            self.db_con.close()

        return process
