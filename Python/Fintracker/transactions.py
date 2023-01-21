from enum import Enum
from typing import Optional

from balance import Balance
from database import Query, Edit
from fintracker import Fintracker, Report
from utils import Utils, Date

# AutoTransactions could use some refactoring


class TransactionType(Enum):
    EXPENSE = "Expense"
    REVENUE = "Revenue"
    BALANCE = "Balance"


class Transactions:
    def __init__(self) -> None:
        self.report = Report()
        self.expenses = Expenses()
        self.balance = Balance()
        self.query_db, self.edit_db = Query(), Edit()
        self.utils, self.date = Utils(), Date()

    def show(
        self, timespan: int, trn_type: TransactionType | None = None
    ) -> None:
        date_limit = self.date.get_limit(timespan)

        if trn_type == TransactionType.EXPENSE:
            df = self.query_db.get_df_with_transactions(
                include_categories=True, filter_trn_type=trn_type.value
            )
        elif trn_type == TransactionType.REVENUE:
            df = self.query_db.get_df_with_transactions(
                filter_trn_type=trn_type.value
            )
        elif trn_type == TransactionType.BALANCE:
            df = self.query_db.get_df_with_transactions(
                filter_trn_type=trn_type.value
            )
        else:
            df = self.query_db.get_df_with_transactions(include_categories=True)

        df = df.loc[df["time"] > date_limit]
        print(df.to_string(index=False))

    def show_summary(self) -> None:
        df = self.query_db.get_df_with_transactions()
        days, date_format = (1, 7, 30), "%Y-%m-%d"
        timespan = [self.date.get_limit(day, date_format) for day in days]

        revenue = [
            self.query_db.get_sum(df, time, "Revenue") for time in timespan
        ]
        expenses = [
            self.query_db.get_sum(df, time, "Expense") for time in timespan
        ]
        net = [(revenue[i] - expenses[i]) for i in range(len(revenue))]
        summary = {
            "Timespan": ["Last 24 hours", "Last 7 days", "Last 30 days"],
            "Revenue": [self.utils.as_currency(val) for val in revenue],
            "Expenses": [self.utils.as_currency(val) for val in expenses],
            "Net": [self.utils.as_currency(val) for val in net],
        }
        self.report.show_transactions_summary(summary)

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
        tid, _, trn_type, amount, note = transaction
        self.edit_db.remove_transaction(tid)

        if trn_type == TransactionType.BALANCE.value:
            self.balance.revert_items_amount(note, amount)
        elif trn_type == TransactionType.EXPENSE.value:
            self.expenses.remove_from_database(tid)
            self.balance.change_cash_amount(amount)
        else:
            self.balance.change_cash_amount(-amount)

    def export_to_csv(self) -> None:
        csv_output = input("Enter csv output path: ")
        if csv_output == "q":
            print("Aborting...")
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
    fintracker, report = Fintracker(), Report()
    transactions = Transactions()
    balance = Balance()
    edit_db = Edit()
    expenses = Expenses()
    utils, date = Utils(), Date()

    def check_for_new(self) -> None:
        new = self._get_new()
        if not new:
            return
        for title, transactions in new.items():
            if len(transactions) == 0:
                continue
            for transaction in transactions:
                self._add(title, transaction)
            self._update_expected_date(title, transactions[-1])
        self.save()
        self.report.show_new_autotransactions(new)

    def _get_new(self) -> dict:
        new = dict()
        for title, info in self.fintracker.auto_transactions.items():
            expected_date = info["expected_date"]
            transactions = list()
            while self.date.is_due(expected_date):
                transaction = dict(info)
                transaction["expected_date"] = expected_date
                transactions.append(transaction)
                delta = self.date.get_delta(info["recurrence"])
                expected_date = self.date.add_delta(expected_date, delta)
            if len(transactions) > 0:
                new[title] = transactions
        return new

    def _add(self, title: str, transaction: dict) -> None:
        time = transaction["expected_date"] + " 00:00:00"
        amount = transaction["expected_amount"]
        if amount < 0:
            trn_type = TransactionType.EXPENSE
        else:
            trn_type = TransactionType.REVENUE

        entry = time, trn_type.value, abs(amount), title.capitalize()
        self._add_to_database(entry)
        if trn_type == TransactionType.EXPENSE:
            # Has to be after adding transaction bc of tid
            expense_category = transaction["category"].capitalize()
            self.expenses.add_to_database(expense_category)

        self.balance.change_cash_amount(amount)

    def _add_to_database(self, entry: tuple) -> None:
        self.edit_db.add_transaction(entry)

    def _update_expected_date(self, title: str, transaction: dict) -> None:
        delta = self.date.get_delta(transaction["recurrence"])
        new_date = self.date.add_delta(transaction["expected_date"], delta)
        self.fintracker.auto_transactions[title]["expected_date"] = new_date

    def save(self) -> None:
        self.fintracker.save_auto_transactions()
