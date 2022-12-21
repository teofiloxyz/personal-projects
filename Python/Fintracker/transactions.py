#!/usr/bin/python3

from Tfuncs import fcol, ffmt
from tabulate import tabulate

import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utils import Utils
from database import Database


class Transactions:
    utils = Utils()
    database = Database()
    json_info = utils.load_json()

    def show_opening_message(self) -> None:
        message = self.auto_transactions()
        if len(message) > 0:
            print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
            print("\n".join(message))
            print()

        balance_negative_items = self.get_balance_negative_items()
        if len(balance_negative_items) > 0:
            for item in balance_negative_items:
                print(
                    f"{ffmt.bold}{fcol.red}{item.capitalize()} "
                    f"is negative!{ffmt.reset}"
                )
            print(
                f"{ffmt.bold}{fcol.red}Please edit the balance "
                f"statement!{ffmt.reset}\n"
            )

        self.summary()

    def get_balance_negative_items(self) -> list[str]:
        # Ñ faço merge aos dicionários pq podem ter items com o mesmo nome
        balance = (
            self.json_info["assets"].items(),
            self.json_info["liabilities"].items(),
        )
        return [
            item
            for category in balance
            for item, amount in category
            if amount < 0
        ]

    def auto_transactions(self) -> list:
        """Posso adicionar expenses também"""
        # need division
        now = self.utils.get_date_now()
        now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        message = list()
        for n, income in enumerate(self.json_info["incomes"].values(), 1):
            date = income["expected_date"]
            date_strp = datetime.strptime(date, "%Y-%m-%d")
            amount = income["expected_amount"]
            income_title = income["title"]
            if now_strp >= date_strp:
                entry = now, "Revenue", amount, income_title
                self.database.Edit().add_transaction(entry)
                if income["recurrence"] == "monthly":
                    delta = relativedelta(months=1)
                else:
                    delta = timedelta(days=7)
                new_date = datetime.strftime(date_strp + delta, "%Y-%m-%d")
                self.json_info["incomes"][str(n)]["expected_date"] = new_date
                # O dinheiro ganho aumenta a rúbrica cash do balanço
                self.json_info["assets"]["cash"] += amount
                self.utils.write_json(self.json_info)

                amount_eur = "€ {:,.2f}".format(amount)
                message.append(f"{amount_eur} from {income_title} was added!")
        return message

    def summary(self) -> None:
        now = self.utils.get_date_now()
        now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        # rework
        df = self.database.Query().create_df_with_transactions()
        date_24h = datetime.strftime(
            now_strp - timedelta(days=1), "%Y-%m-%d %H:%M:%S"
        )
        date_7d = datetime.strftime(
            now_strp - timedelta(days=7), "%Y-%m-%d %H:%M:%S"
        )
        date_30d = datetime.strftime(
            now_strp - timedelta(days=30), "%Y-%m-%d %H:%M:%S"
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

        # need a loop
        values = {
            "Timespan": ["Last 24 hours", "Last 7 days", "Last 30 days"],
            "Revenue": [
                self.utils.get_val_as_currency(revenue_24h),
                self.utils.get_val_as_currency(revenue_7d),
                self.utils.get_val_as_currency(revenue_30d),
            ],
            "Expenses": [
                self.utils.get_val_as_currency(expenses_24h),
                self.utils.get_val_as_currency(expenses_7d),
                self.utils.get_val_as_currency(expenses_30d),
            ],
            "Balance": [
                self.utils.get_val_as_currency(balance_24h),
                self.utils.get_val_as_currency(balance_7d),
                self.utils.get_val_as_currency(balance_30d),
            ],
        }
        table = tabulate(
            values, headers="keys", tablefmt="fancy_grid", stralign="center"
        )
        print(table)

    def show(self, option: str, timespan: str) -> None:
        # improve
        if option == "all":
            df = self.database.Query().create_df_with_transactions()
        elif option == "expenses":
            df = self.database.Query().create_df_with_expenses()
        elif option == "revenue":
            df = self.database.Query().create_df_with_revenue()

        if type(timespan) != "int":
            try:
                timespan = int(timespan)
            except ValueError:
                print("Must enter an integer...")
                return

        now = self.utils.get_date_now()
        now_strp = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        date_limit = datetime.strftime(
            now_strp - timedelta(days=timespan), "%Y-%m-%d %H:%M:%S"
        )
        df = df.loc[df["time"] > date_limit]
        print(df.to_string(index=False))

    def add(self) -> None:
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
                    "\nEnter category # (or enter custom name): "
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
                        self.utils.write_json(self.json_info)
                        break

        note = input("Enter a note (leave empty for none): ")
        if note == "q":
            print("Aborting...")
            return

        if trn_type == "Expense":
            self.json_info["assets"]["cash"] -= amount
        else:
            self.json_info["assets"]["cash"] += amount
        self.utils.write_json(self.json_info)

        entry = now, trn_type, amount, note
        self.database.Edit().add_transaction(entry)

        last_transaction = self.database.Query().get_last_transaction()
        if trn_type == "Expense":
            trn_id = last_transaction[0]
            self.database.Edit().add_expense(category, trn_id)

        if self.json_info["assets"]["cash"] < 0:
            print(
                f"{ffmt.bold}{fcol.red}You got negative cash, please edit "
                f"the balance statement!{ffmt.reset}"
            )

    def remove(self) -> None:
        df = self.database.Query().create_df_with_transactions()
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
                no_errors = [
                    self.remove_transaction(trn_id) for trn_id in selected_id
                ]
            else:
                no_errors = self.remove_transaction(selected_id)
            if no_errors:
                break

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        # put in utils
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

    def add_transaction(self, entry: tuple) -> None:
        self.database.Edit().add_transaction(entry)

    def remove_transaction(self, tid: str) -> None:
        try:
            tid = int(tid)
        except ValueError:
            print("Must enter an integer...")
            return

        trn_id_fetch = self.database.Query().get_transaction_from_id(tid)
        if trn_id_fetch is None:
            print(f"Transaction with id '{tid}' not found on database!")
            return

        trn_type, amount, note = (
            trn_id_fetch[2],
            trn_id_fetch[3],
            trn_id_fetch[4],
        )

        if trn_id_fetch[2] != "Expense":
            self.database.Edit().remove_transaction(tid)
            return

        # Correct the balance statement
        self.database.Edit().remove_transaction(tid, is_expense=True)
        if trn_type == "Balance":

            note_1 = re.sub(" [-+][la]:.*$", "", note)
            note_2 = note.replace(note_1, "").strip()

            self.change_balance_item(note_1, amount)
            # if not isolated balance change to be reversed
            if note_2 != "":
                self.change_balance_item(note_2, amount)

        elif trn_type == "Expense":
            self.json_info["assets"]["cash"] += amount
        else:
            self.json_info["assets"]["cash"] -= amount
        self.utils.write_json(self.json_info)

    def change_balance_item(self, entry: str, amount: float) -> None:
        category = "assets" if entry[1] == "a" else "liabilities"
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
