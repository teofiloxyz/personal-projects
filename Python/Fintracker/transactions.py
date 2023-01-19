import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

import re
from enum import Enum

from fintracker import Fintracker
from utils import Utils, Date
from database import Query, Edit


class TransactionType(Enum):
    EXPENSE = "Expense"
    REVENUE = "Revenue"
    BALANCE = "Balance"


class Transactions:
    fintracker = Fintracker()
    utils, date = Utils(), Date()
    query_db, edit_db = Query(), Edit()

    def show(self, option: str, timespan: str) -> None:
        try:
            date_limit = self.date.get_limit(int(timespan))
        except ValueError:
            print("Must enter an integer...")
            return

        if option == TransactionType.EXPENSE:
            df = self.query_db.create_df_with_expenses()
        elif option == TransactionType.REVENUE:
            df = self.query_db.create_df_with_revenue()
        else:
            df = self.query_db.create_df_with_transactions()

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
            categories = self.query_db.get_categories()
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

    def add_entry(self, entry: tuple) -> None:
        self.edit_db.add_transaction(entry)

    def remove(self) -> None:
        df = self.query_db.create_df_with_transactions()
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

    def remove_entry(self, transaction: tuple) -> None:
        tid, _, trn_type, amount, note = transaction
        if trn_type == "Expense":
            self.edit_db.remove_transaction(tid, is_expense=True)
            self.fintracker.balance["assets"]["cash"] += amount
        elif trn_type == "Revenue":
            self.edit_db.remove_transaction(tid)
            self.fintracker.balance["assets"]["cash"] -= amount
        elif trn_type == "Balance":
            self.edit_db.remove_transaction(tid)
            item_1 = re.sub(" [-+][la]:.*$", "", note)
            self.change_balance_item(item_1, amount)
            item_2 = note.replace(item_1, "").strip()
            # if not isolated balance transaction, change to be reversed
            if item_2 != "":
                self.change_balance_item(item_2, amount)
        self.fintracker.save()

    def get_transactions_from_tids(self, tids: list) -> list | None:
        transactions = list()
        for tid in tids:
            try:
                tid = int(tid)
            except ValueError:
                print(f"Can't process '{tid}', try again...")
                return

            transaction = self.query_db.get_transaction_from_id(tid)
            if transaction is None:
                print(f"Transaction with id '{tid}' not found on database!")
                return
            transactions.append(transaction)
        return transactions

    def export_to_csv(self) -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return
        self.query_db.export_transactions_to_csv(csv_output)


class Expenses(Transactions):
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

    def add_expense_entry(self, category: str) -> None:
        trn_id = self.query_db.get_last_transaction()[0]
        self.edit_db.add_expense(category, trn_id)


class AutoTransactions(Transactions):
    def check_for_new(self) -> None:
        new = self.get_new()
        if new:
            self.add_to_database(new)
            self.update_dates(new)
            self.update_cash_on_balance(new)  # esta fica fora
            self.show(new)

    def get_new(self) -> list:
        auto_transactions = []
        for title, transaction in self.fintracker.auto_transactions:
            if self.date.is_due(transaction["expected_date"]):
                auto_transactions.append(transaction)
        return auto_transactions

    def add_to_database(self, new: list) -> None:
        for transaction in new:
            now = self.date.get_now()
            entry = (now, transaction["type"], transaction["amount"], title)
            self.edit_db.add_transaction(entry)

    def update_dates(self, new: list) -> None:
        for transaction in new:
            now = self.date.get_now()
            delta = self.date.get_delta(transaction["recurrence"])
            new_date = self.date.add_delta(now, delta)
            self.fintracker.auto_transactions[transaction["title"]][
                "expected_date"
            ] = new_date
            self.fintracker.save()

    def show(self, new: list) -> None:
        print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
        print("\n".join(new))
        print()


class Charts:
    date = Date()
    db_query = Query()

    def show(self) -> None:
        plt.style.use("dark_background")
        options = {
            "1": (
                "Revenue of last 30 days",
                lambda: self.show_time_chart_by_trn_type("Revenue"),
            ),
            "2": (
                "Expenses of last 30 days",
                lambda: self.show_time_chart_by_trn_type("Expenses"),
            ),
            "3": (
                "Category percentage of expenses of last 30 days",
                self.show_pie_chart_expenses_cat,
            ),
        }
        while True:
            [print(f"[{n}] {option[0]}") for n, option in options.items()]
            selection = input("\nEnter the chart option: ")
            if selection == "q":
                print("Aborting...")
                return
            try:
                options[selection][1]()
                break
            except KeyError:
                continue

    def show_pie_chart_expenses_cat(self) -> None:
        df = self.db_query.create_df_with_expenses(
            selection="SUBSTR(time, 1, 10) as date, amount, category"
        )
        date_limit = self.date.get_date_limit(days=30)
        df = df.loc[df["date"] > date_limit]
        categories_list = df["category"].unique().tolist()
        amounts_list = list()
        for category in categories_list:
            amount = df.loc[df["category"] == category]["amount"].sum()
            amounts_list.append(amount)

        plt.pie(
            np.array(amounts_list),
            labels=categories_list,
            autopct="%1.1f%%",
        )
        plt.show()

    def show_time_chart_by_trn_type(self, trn_type: str) -> None:
        print(f"Showing {trn_type} chart...")
        if trn_type == "Expenses":
            df = self.db_query.create_df_with_expenses(
                selection="SUBSTR(time, 1, 10) as date, amount"
            )
        else:
            df = self.db_query.create_df_with_revenue(
                selection="SUBSTR(time, 1, 10) as date, amount"
            )
        date_limit = self.date.get_date_limit(days=30)
        df = df.loc[df["date"] > date_limit].groupby("date")["amount"].sum()

        df.plot(x="date", y="amount", kind="line")
        plt.legend(title=trn_type)
        plt.show()


class Balan:
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

    def change_balance_cash_amount(self, trn_type: str, amount: float) -> None:
        if trn_type == "Expense":
            self.fintracker.balance["assets"]["cash"] -= amount
        else:
            self.fintracker.balance["assets"]["cash"] += amount
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


class extra:
    def show_opening_message(self) -> None:
        self.check_for_balance_negative_items()
        self.show_summary()

    def show_summary(self) -> None:
        df = self.query_db.create_df_with_transactions()
        days, date_format = (1, 7, 30), "%Y-%m-%d"
        timespan = [self.date.get_limit(day, date_format) for day in days]

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
