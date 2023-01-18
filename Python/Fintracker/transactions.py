import pandas as pd
from Tfuncs import fcol, ffmt
from tabulate import tabulate

import re

from fintracker import Fintracker
from utils import Utils, Date
from database import Query, Edit


class Transactions:
    fintracker = Fintracker()
    utils, date = Utils(), Date()
    db_query, db_edit = Query(), Edit()

    def show_opening_message(self) -> None:
        self.check_for_new_auto_transactions()
        self.check_for_balance_negative_items()
        self.show_summary()

    def check_for_new_auto_transactions(self) -> None:
        new_auto_transactions = self.auto_transactions()
        if len(new_auto_transactions) > 0:
            self.show_new_auto_transactions(new_auto_transactions)

    def auto_transactions(self) -> list:
        """Posso adicionar expenses também"""
        message = list()
        for title, income in self.fintracker.auto_transactions[
            "incomes"
        ].items():
            if not self.date.date_is_due(income["expected_date"]):
                continue

            now = self.date.get_date_now("%Y-%m-%d %H:%M:%S")
            amount = income["expected_amount"]
            entry = now, "Revenue", amount, title
            self.add_entry(entry)

            delta = self.date.get_date_delta(income["recurrence"])
            new_date = self.date.add_delta_to_date(
                now, delta, date_format="%Y-%m-%d %H:%M:%S"
            )
            self.fintracker.auto_transactions["incomes"][title][
                "expected_date"
            ] = new_date
            # O dinheiro ganho aumenta a rubrica cash do balanço
            self.fintracker.balance["assets"]["cash"] += amount
            self.fintracker.save()

            message.append(
                f"{self.utils.get_val_as_currency(amount)} from {title} was added!"
            )
        return message

    def show_new_auto_transactions(self, new_auto_transactions: list) -> None:
        print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
        print("\n".join(new_auto_transactions))
        print()

    def check_for_balance_negative_items(self) -> None:
        balance_negative_items = self.get_balance_negative_items()
        if len(balance_negative_items) > 0:
            self.show_balance_negative_items(balance_negative_items)

    def get_balance_negative_items(self) -> list[str]:
        return [
            item
            for category in self.fintracker.balance.values()
            for item, amount in category.items()
            if amount < 0
        ]

    def show_balance_negative_items(self, balance_negative_items: list) -> None:
        for item in balance_negative_items:
            print(
                f"{ffmt.bold}{fcol.red}{item.capitalize()} is negative!{ffmt.reset}"
            )
        print(
            f"{ffmt.bold}{fcol.red}Please edit the balance statement!{ffmt.reset}\n"
        )

    def show_summary(self) -> None:
        df = self.db_query.create_df_with_transactions()
        days, date_format = (1, 7, 30), "%Y-%m-%d"
        timespan = [self.date.get_date_limit(day, date_format) for day in days]

        revenue = [self.get_trns_sum(df, time, "Revenue") for time in timespan]
        expenses = [self.get_trns_sum(df, time, "Expense") for time in timespan]
        balance = [(revenue[i] - expenses[i]) for i in range(len(revenue))]

        summary = {
            "Timespan": ["Last 24 hours", "Last 7 days", "Last 30 days"],
            "Revenue": [self.utils.get_val_as_currency(x) for x in revenue],
            "Expenses": [self.utils.get_val_as_currency(x) for x in expenses],
            "Balance": [self.utils.get_val_as_currency(x) for x in balance],
        }

        table = tabulate(
            summary, headers="keys", tablefmt="fancy_grid", stralign="center"
        )
        print(table)

    def get_trns_sum(self, df: pd.DataFrame, time: str, trn_type: str) -> int:
        return (
            df[(df["time"] > time) & (df["trn_type"] == trn_type)].sum().amount
        )

    def show(self, option: str, timespan: str) -> None:
        try:
            date_limit = self.date.get_date_limit(int(timespan))
        except ValueError:
            print("Must enter an integer...")
            return

        if option == "expenses":
            df = self.db_query.create_df_with_expenses()
        elif option == "revenue":
            df = self.db_query.create_df_with_revenue()
        else:
            df = self.db_query.create_df_with_transactions()

        df = df.loc[df["time"] > date_limit]
        print(df.to_string(index=False))

    def add(self) -> None:
        while True:
            amount = input(
                "Enter amount of the expense (e.g.: 100.55 or "
                "+100.55 if revenue): "
            )
            if amount == "q":
                print("Aborting...")
                return

            # Most of the transactions will be expenses
            trn_type = "Revenue" if amount.startswith("+") else "Expense"
            try:
                amount = round(float(amount), 2)
            except ValueError:
                print("Value error, try again...")
                continue
            break

        if trn_type == "Expense":
            categories = self.db_query.get_categories()
            category = self.choose_expense_category(categories)
            if category == "q":
                print("Aborting...")
                return

        note = input("Enter a note (leave empty for none): ")
        if note == "q":
            print("Aborting...")
            return

        self.change_balance_cash_amount(trn_type, amount)

        now = self.date.get_date_now("%Y-%m-%d %H:%M:%S")
        entry = now, trn_type, amount, note
        self.add_entry(entry)
        if trn_type == "Expense":
            self.add_expense_entry(category)

        self.check_for_balance_negative_items()  # Check if cash is negative

    def choose_expense_category(self, categories: list) -> str:
        while True:
            [
                print(f"[{n}] {category}")
                for n, category in enumerate(categories, 1)
            ]
            category = input(
                "\nEnter category # (or enter custom name): "
            ).capitalize()
            if category in ("Q", ""):
                return "q"
            elif category in categories:
                print("Category already in list...")
            else:
                try:
                    category = categories[int(category) - 1]
                    return category
                except IndexError:
                    print("Index outside the list...")
                except ValueError:
                    return category

    def change_balance_cash_amount(self, trn_type: str, amount: float) -> None:
        if trn_type == "Expense":
            self.fintracker.balance["assets"]["cash"] -= amount
        else:
            self.fintracker.balance["assets"]["cash"] += amount
        self.fintracker.save()

    def add_entry(self, entry: tuple) -> None:
        self.db_edit.add_transaction(entry)

    def add_expense_entry(self, category: str) -> None:
        trn_id = self.db_query.get_last_transaction()[0]
        self.db_edit.add_expense(category, trn_id)

    def remove(self) -> None:
        df = self.db_query.create_df_with_transactions()
        print(df.to_string(index=False))

        while True:
            selected_id = input(
                "\nEnter the transaction_id to remove or "
                "several (e.g.: 30+4+43): "
            )
            if selected_id == "q":
                print("Aborting...")
                return
            else:
                tids = selected_id.split("+")
            transactions = self.get_transactions_from_tids(tids)
            if transactions is not None:
                break

        [self.remove_entry(transaction) for transaction in transactions]
        self.check_for_balance_negative_items()

    def get_transactions_from_tids(self, tids: list) -> list | None:
        transactions = list()
        for tid in tids:
            try:
                tid = int(tid)
            except ValueError:
                print(f"Can't process '{tid}', try again...")
                return

            transaction = self.db_query.get_transaction_from_id(tid)
            if transaction is None:
                print(f"Transaction with id '{tid}' not found on database!")
                return
            transactions.append(transaction)
        return transactions

    def remove_entry(self, transaction: tuple) -> None:
        tid, _, trn_type, amount, note = transaction
        if trn_type == "Expense":
            self.db_edit.remove_transaction(tid, is_expense=True)
            self.fintracker.balance["assets"]["cash"] += amount
        elif trn_type == "Revenue":
            self.db_edit.remove_transaction(tid)
            self.fintracker.balance["assets"]["cash"] -= amount
        elif trn_type == "Balance":
            self.db_edit.remove_transaction(tid)
            item_1 = re.sub(" [-+][la]:.*$", "", note)
            self.change_balance_item(item_1, amount)
            item_2 = note.replace(item_1, "").strip()
            # if not isolated balance transaction, change to be reversed
            if item_2 != "":
                self.change_balance_item(item_2, amount)
        self.fintracker.save()

    def change_balance_item(self, entry: str, amount: float) -> None:
        category = "assets" if entry[1] == "a" else "liabilities"
        item = entry[3:]
        operation = entry[0]

        item_val = (
            self.fintracker.balance[category][item]
            if item in self.fintracker.balance[category].keys()
            else 0
        )
        if operation == "+":
            # Reversed bc removed transaction
            self.fintracker.balance[category][item] = item_val - amount
        else:
            self.fintracker.balance[category][item] = item_val + amount

    def export_csv(self) -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return
        self.db_query.export_transactions_to_csv(csv_output)
