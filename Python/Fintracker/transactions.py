import numpy as np
import matplotlib.pyplot as plt

from enum import Enum
from typing import Optional

from fintracker import Fintracker
from balance import Balance
from database import Query, Edit
from utils import Utils, Date


class TransactionType(Enum):
    EXPENSE = "Expense"
    REVENUE = "Revenue"
    BALANCE = "Balance"


class Transactions:
    def __init__(self) -> None:
        self.expenses = Expenses()
        self.balance = Balance()
        self.query_db, self.edit_db = Query(), Edit()
        self.utils, self.date = Utils(), Date()

    def show(
        self, timespan: int, option: TransactionType | None = None
    ) -> None:
        date_limit = self.date.get_limit(timespan)

        if option == TransactionType.EXPENSE:
            df = self.query_db.create_df_with_expenses()
        elif option == TransactionType.REVENUE:
            df = self.query_db.create_df_with_revenue()
        else:
            df = self.query_db.create_df_with_transactions()

        df = df.loc[df["time"] > date_limit]
        print(df.to_string(index=False))

    def add(self) -> None:
        prompt_amount = self._get_amount()
        if not prompt_amount:
            print("Aborting...")
            return

        amount = round(float(prompt_amount), 2)
        trn_type = self._get_trn_type(prompt_amount)
        if trn_type == TransactionType.EXPENSE:
            expense_category = self._get_expense_category()
            if not expense_category:
                print("Aborting...")
                return

        note = self._get_note()
        if note == "q":
            print("Aborting...")
            return

        now = self.date.get_now("%Y-%m-%d %H:%M:%S")
        transaction = now, trn_type.value, amount, note
        self._add_to_database(transaction)

        if trn_type == TransactionType.EXPENSE:
            self.expenses.add_to_database(expense_category)
            self.balance.change_cash_amount(-amount)
        else:
            self.balance.change_cash_amount(amount)

    def _get_amount(self) -> Optional[str]:
        while True:
            prompt = input(
                "Enter amount of the expense (e.g.: 100.55 or "
                "+100.55 if revenue): "
            )
            if prompt == "q":
                print("Aborting...")
                return None
            try:
                round(float(prompt), 2)
                return prompt
            except ValueError:
                print("Value error, try again...")

    def _get_trn_type(self, prompt: str) -> TransactionType:
        if prompt.startswith("+"):
            return TransactionType.REVENUE
        else:
            return TransactionType.EXPENSE

    def _get_expense_category(self) -> Optional[str]:
        return self.expenses.choose_category()

    def _get_note(self) -> str:
        return input("Enter a note (leave empty for none): ")

    def _add_to_database(self, entry: tuple) -> None:
        self.edit_db.add_transaction(entry)

    def remove(self) -> None:
        self.show(timespan=365)

        tids = self._get_tids()
        if not tids:
            print("Aborting...")
            return

        transactions = self._get_transactions_from_tids(tids)
        if not transactions:
            print("Aborting...")
            return

        [self._remove_from_database(trn) for trn in transactions]

    def _get_tids(self) -> Optional[list[int]]:
        while True:
            prompt = input(
                "\nEnter the transaction_id to remove or "
                "several (e.g.: 30+4+43): "
            )
            if prompt == "q":
                return None
            try:
                return [int(tid) for tid in prompt.split("+")]
            except ValueError:
                print("Invalid input, try again...")

    def _get_transactions_from_tids(self, tids: list) -> Optional[list]:
        transactions = [
            self.query_db.get_transaction_from_id(tid)
            for tid in tids
            if self.query_db.get_transaction_from_id(tid) is not None
        ]
        if not transactions:
            print("Please, provide valid ids...")
        return transactions

    def _remove_from_database(self, transaction: tuple) -> None:
        tid, _, trn_type, amount, _ = transaction
        self.edit_db.remove_transaction(tid)

        if trn_type == TransactionType.BALANCE.value:
            self.balance.change_item_amount(transaction)
        if trn_type == TransactionType.EXPENSE.value:
            self.expenses.remove_from_database(tid)
            self.balance.change_cash_amount(-amount)
        else:
            self.balance.change_cash_amount(amount)

    def export_to_csv(self) -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborted...")
            return
        self.query_db.export_transactions_to_csv(csv_output)


class Expenses:
    query_db, edit_db = Query(), Edit()

    def add_to_database(self, category: str) -> None:
        tid = self.query_db.get_last_transaction()[0]
        self.edit_db.add_expense(category, tid)

    def remove_from_database(self, tid: int) -> None:
        self.edit_db.remove_expense(tid)

    def choose_category(self) -> Optional[str]:
        categories = self.query_db.get_expense_categories()
        prompt = "\nEnter category # (or enter custom name): "
        return self._validate_category(categories, prompt)

    def _validate_category(
        self, categories: list[str], prompt: str
    ) -> Optional[str]:
        while True:
            for n, category in enumerate(categories, 1):
                print(f"[{n}] {category}")

            choice = input(prompt).strip()
            if choice.lower() == "q":
                return None
            elif choice.isdigit():
                try:
                    return categories[int(choice) - 1]
                except IndexError:
                    print("Invalid category number, try again...")
            else:
                return choice


class AutoTransactions:
    fintracker = Fintracker()
    transactions = Transactions()
    balance = Balance()
    edit_db = Edit()
    expenses = Expenses()
    utils, date = Utils(), Date()

    def check_for_new(self) -> None:
        new = self._get_new()
        if not new:
            return
        for title, transaction in new.items():
            self._add(title, transaction)
            self._update_expected_date(title, transaction)
            # self.fintracker.show()

    def _get_new(self) -> dict:
        new = dict()
        for title, info in self.fintracker.auto_transactions.items():
            if self.date.is_due(info["expected_date"]):
                new[title] = info
        return new

    def _add(self, title: str, transaction: dict) -> None:
        time = transaction["expected_date"] + " 00:00:00"
        amount = transaction["expected_amount"]
        if amount < 0:
            trn_type = TransactionType.EXPENSE
        else:
            trn_type = TransactionType.REVENUE

        entry = time, trn_type.value, abs(amount), title
        self._add_to_database(entry)
        if trn_type == TransactionType.EXPENSE:
            # Has to be after adding transaction
            expense_category = transaction["recurrence"]
            self.expenses.add_to_database(expense_category)

        self.balance.change_cash_amount(amount)

    def _add_to_database(self, entry: tuple) -> None:
        self.edit_db.add_transaction(entry)

    def _update_expected_date(self, title: str, transaction: dict) -> None:
        delta = self.date.get_delta(transaction["recurrence"])
        new_date = self.date.add_delta(transaction["expected_date"], delta)
        self.fintracker.auto_transactions[title]["expected_date"] = new_date


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
        date_limit = self.date.get_limit(days=30)
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
        date_limit = self.date.get_limit(days=30)
        df = df.loc[df["date"] > date_limit].groupby("date")["amount"].sum()

        df.plot(x="date", y="amount", kind="line")
        plt.legend(title=trn_type)
        plt.show()
