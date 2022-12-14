#!/usr/bin/python3


class Transactions:
    def opening_message(self):
        if len(self.message) != 0:
            print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
            print("\n".join(self.message))
            print()

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        balance = (
            self.json_info["assets"].items(),
            self.json_info["liabilities"].items(),
        )
        for items in balance:
            for item, amount in items:
                if amount < 0:
                    need_to_edit_balance = True
                    print(
                        f"{ffmt.bold}{fcol.red}{item.capitalize()} "
                        f"is negative!{ffmt.reset}"
                    )

        if need_to_edit_balance:
            print(
                f"{ffmt.bold}{fcol.red}Please edit the balance "
                f"statement!{ffmt.reset}\n"
            )

        self.summary()

    def auto_transactions(self):
        # Posso adicionar expenses também
        for n, income in enumerate(self.json_info["incomes"].values(), 1):
            date = income["expected_date"]
            date_strp = datetime.strptime(date, "%Y-%m-%d")
            amount = income["expected_amount"]
            income_title = income["title"]
            if self.now_strp >= date_strp:
                entry = self.now, "Revenue", amount, income_title
                self.cursor.execute(
                    "INSERT INTO transactions (time, "
                    f"trn_type, amount, note) VALUES {entry}"
                )
                self.db_con.commit()

                if income["recurrence"] == "monthly":
                    delta = relativedelta(months=1)
                else:
                    delta = timedelta(days=7)
                new_date = datetime.strftime(date_strp + delta, "%Y-%m-%d")
                self.json_info["incomes"][str(n)]["expected_date"] = new_date
                # O dinheiro ganho aumenta a rúbrica cash do balanço
                self.json_info["assets"]["cash"] += amount
                self.save_json()

                amount_eur = "€ {:,.2f}".format(amount)
                self.message.append(
                    f"{amount_eur} from {income_title} " "was added!"
                )

    def show_transactions(self, option, timespan):
        if option == "all":
            df = pd.read_sql(
                "SELECT * FROM transactions LEFT JOIN "
                "expenses USING(transaction_id)",
                self.db_con,
            )
        elif option == "expenses":
            df = pd.read_sql(
                "SELECT * FROM transactions LEFT JOIN "
                "expenses USING(transaction_id) WHERE "
                'trn_type = "Expense"',
                self.db_con,
            )
        elif option == "revenue":
            df = pd.read_sql(
                "SELECT * FROM transactions WHERE " 'trn_type = "Revenue"',
                self.db_con,
            )

        if type(timespan) != "int":
            try:
                timespan = int(timespan)
            except ValueError:
                print("Must enter an integer...")
                return

        date_limit = datetime.strftime(
            self.now_strp - timedelta(days=timespan), "%Y-%m-%d %H:%M:%S"
        )
        df = df.loc[df["time"] > date_limit]
        print(df.to_string(index=False))

    def summary(self):
        df = pd.read_sql("SELECT * FROM transactions", self.db_con)
        date_24h = datetime.strftime(
            self.now_strp - timedelta(days=1), "%Y-%m-%d %H:%M:%S"
        )
        date_7d = datetime.strftime(
            self.now_strp - timedelta(days=7), "%Y-%m-%d %H:%M:%S"
        )
        date_30d = datetime.strftime(
            self.now_strp - timedelta(days=30), "%Y-%m-%d %H:%M:%S"
        )

        revenue_24h = (
            df[(df["time"] > date_24h) & (df["trn_type"] == "Revenue")]
            .sum()
            .amount
        )
        expenses_24h = (
            df[(df["time"] > date_24h) & (df["trn_type"] == "Expense")]
            .sum()
            .amount
        )
        balance_24h = revenue_24h - expenses_24h

        revenue_7d = (
            df[(df["time"] > date_7d) & (df["trn_type"] == "Revenue")]
            .sum()
            .amount
        )
        expenses_7d = (
            df[(df["time"] > date_7d) & (df["trn_type"] == "Expense")]
            .sum()
            .amount
        )
        balance_7d = revenue_7d - expenses_7d

        revenue_30d = (
            df[(df["time"] > date_30d) & (df["trn_type"] == "Revenue")]
            .sum()
            .amount
        )
        expenses_30d = (
            df[(df["time"] > date_30d) & (df["trn_type"] == "Expense")]
            .sum()
            .amount
        )
        balance_30d = revenue_30d - expenses_30d

        values = {
            "Revenue": [revenue_24h, revenue_7d, revenue_30d],
            "Expenses": [expenses_24h, expenses_7d, expenses_30d],
            "Balance": [balance_24h, balance_7d, balance_30d],
        }
        timespan = ["Last 24 hours", "Last 7 days", "Last 30 days"]
        print(pd.DataFrame(data=values, index=timespan))

    def add_transaction(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        while True:
            amount = input(
                "Enter amount of the expense (e.g.: 100.55 or "
                "+100.55 if revenue): "
            )
            if amount == "q":
                print("Aborting...")
                return
            if amount.startswith("-"):
                continue
            # Most of the transactions will be expenses
            trn_type = "Revenue" if amount.startswith("+") else "Expense"
            try:
                amount = round(float(amount), 2)
            except ValueError:
                print("Value error, try again: ")
                continue
            break

        if trn_type == "Expense":
            categories = self.json_info["expenses_categories"]
            [
                print(f"[{n}] {category}")
                for n, category in enumerate(categories, 1)
            ]
            while True:
                category = input(
                    "\nEnter category # (or enter " "custom name): "
                ).capitalize()
                if category in ("Q", ""):
                    print("Aborting...")
                    return
                elif category in categories:
                    print("Category already in list...")
                else:
                    try:
                        category = categories[int(category) - 1]
                        break
                    except IndexError:
                        print("Index outside the list...")
                    except ValueError:
                        self.json_info["expenses_categories"].append(category)
                        self.save_json()
                        break

        note = input("Enter a note (leave empty for none): ")
        if note == "q":
            print("Aborting...")
            return

        if trn_type == "Expense":
            self.json_info["assets"]["cash"] -= amount
        else:
            self.json_info["assets"]["cash"] += amount
        self.save_json()

        entry = now, trn_type, amount, note
        self.cursor.execute(
            "INSERT INTO transactions (time, trn_type, "
            f"amount, note) VALUES {entry}"
        )
        self.db_con.commit()

        self.cursor.execute(
            "SELECT * FROM transactions ORDER BY " "transaction_id DESC LIMIT 1"
        )
        last = self.cursor.fetchone()
        if last[1:] == entry:
            print("Transaction successfuly saved on database!")
        else:
            print("Database error! Transaction not saved!")

        if trn_type == "Expense":
            trn_id = last[0]
            self.cursor.execute(
                "INSERT INTO expenses (transaction_id, "
                f"category) VALUES {trn_id, category}"
            )
            self.db_con.commit()

        if self.json_info["assets"]["cash"] < 0:
            print(
                f"{ffmt.bold}{fcol.red}You got negative cash, please edit "
                f"the balance statement!{ffmt.reset}"
            )

    def remove_transaction(self):
        def remove(trn_id):
            try:
                trn_id = int(trn_id)
            except ValueError:
                print("Must enter an integer...")
                return False

            self.cursor.execute(
                "SELECT * FROM transactions WHERE " f"transaction_id = {trn_id}"
            )
            trn_id_fetch = self.cursor.fetchone()
            if trn_id_fetch is None:
                print(f"Transaction with id '{trn_id}' not found on database!")
                return False

            trn_type, amount, note = (
                trn_id_fetch[2],
                trn_id_fetch[3],
                trn_id_fetch[4],
            )

            self.cursor.execute(
                "DELETE FROM transactions WHERE " f"transaction_id = {trn_id}"
            )
            if trn_id_fetch[2] == "Expense":
                self.cursor.execute(
                    "DELETE FROM expenses WHERE " f"transaction_id = {trn_id}"
                )
            self.db_con.commit()

            self.cursor.execute(
                "SELECT * FROM transactions WHERE " f"transaction_id = {trn_id}"
            )
            trn_id_fetch = self.cursor.fetchone()
            if trn_id_fetch is None:
                print(
                    f"Transaction with id '{trn_id}' successfuly removed "
                    "from database!"
                )
                # Correct the balance statement
                if trn_type == "Balance":

                    def change_balance_item(entry):
                        category = (
                            "assets" if entry[1] == "a" else "liabilities"
                        )
                        item = entry[3:]
                        operation = entry[0]

                        item_val = (
                            self.json_info[category][item]
                            if item in self.json_info[category].keys()
                            else 0
                        )
                        if operation == "+":
                            # Reversed bc removed transaction
                            self.json_info[category][item] = item_val - amount
                        else:
                            self.json_info[category][item] = item_val + amount

                    note_1 = re.sub(" [-+][la]:.*$", "", note)
                    note_2 = note.replace(note_1, "").strip()

                    change_balance_item(note_1)
                    # if not isolated balance change to be reversed
                    if note_2 != "":
                        change_balance_item(note_2)

                elif trn_type == "Expense":
                    self.json_info["assets"]["cash"] += amount
                else:
                    self.json_info["assets"]["cash"] -= amount
                self.save_json()
            else:
                print(
                    f"Database error! Transaction with id '{trn_id}' was "
                    "not removed!"
                )
            return True

        df = pd.read_sql(
            "SELECT * FROM transactions LEFT JOIN expenses "
            "USING(transaction_id)",
            self.db_con,
        )
        print(df.to_string(index=False))
        while True:
            selected_id = input(
                "\nEnter the transaction_id to remove or "
                "several (e.g.: 30+4+43): "
            )
            if selected_id == "q":
                print("Aborting...")
                return
            elif "+" in selected_id:
                selected_id = selected_id.split("+")
                no_errors = [remove(trn_id) for trn_id in selected_id]
            else:
                no_errors = remove(selected_id)
            if no_errors:
                break

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        balance = (
            self.json_info["assets"].items(),
            self.json_info["liabilities"].items(),
        )
        for items in balance:
            for item, amount in items:
                if amount < 0:
                    need_to_edit_balance = True
                    print(
                        f"{ffmt.bold}{fcol.red}{item.capitalize()} "
                        f"is negative!{ffmt.reset}"
                    )

        if need_to_edit_balance:
            print(
                f"{ffmt.bold}{fcol.red}Please edit the balance "
                f"statement!{ffmt.reset}"
            )
