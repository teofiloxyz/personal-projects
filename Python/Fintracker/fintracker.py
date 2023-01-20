from tabulate import tabulate

from utils import Utils


class Fintracker:
    def __init__(self) -> None:
        self.auto_transactions: dict = Utils().load_json(
            "auto_transactions.json"
        )
        self.balance: dict = Utils().load_json("balance.json")

    def save(self) -> None:
        Utils().write_json("auto_transactions.json", self.auto_transactions)
        Utils().write_json("balance.json", self.balance)


# put in the main.py?
class Messages:
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

    def show_balance(self, balance) -> None:
        table = tabulate(
            balance,
            headers=("Item", "Amount"),
            tablefmt="fancy_grid",
            stralign="center",
        )
        print(table)

    def show_balance_negative_items(self, balance_negative_items: list) -> None:
        for item in balance_negative_items:
            print(f"{item.capitalize()} is negative!")
        print("Please edit the balance statement!\n")

    def show(self, new: list) -> None:
        print("New Message:")
        print("\n".join(new))
        print()
