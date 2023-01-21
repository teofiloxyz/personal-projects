import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

from database import Query
from utils import Utils, Date


class Fintracker:
    def __init__(self) -> None:
        self.auto_transactions: dict = Utils().load_json(
            "auto_transactions.json"
        )
        self.balance: dict = Utils().load_json("balance.json")

    def save_auto_transactions(self) -> None:
        Utils().write_json("auto_transactions.json", self.auto_transactions)

    def save_balance(self, balance: dict) -> None:
        Utils().write_json("balance.json", balance)


class Report:
    def show_transactions_summary(self, summary: dict) -> None:
        print("Transactions Summary:")
        table = tabulate(
            summary, headers="keys", tablefmt="fancy_grid", stralign="center"
        )
        print(table)

    def show_new_autotransactions(self, new_autotransactions: dict) -> None:
        print("New Auto-transactions:")
        for title, transactions in new_autotransactions.items():
            for transaction in transactions:
                date = transaction["expected_date"]
                amount = Utils().as_currency(transaction["expected_amount"])
                print(f"{date}: {title.capitalize()}: {amount}")
        print()

    def show_balance(self, balance) -> None:
        table = tabulate(
            balance,
            headers=("Item", "Amount"),
            tablefmt="fancy_grid",
            stralign="center",
        )
        print(table)

    def show_negative_item(self, item: str, amount: float) -> None:
        print(
            f"{item} is negative: {Utils().as_currency(amount)}"
            "\nPlease edit the balance statement!\n"
        )

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
            df = self.db_query.get_df_with_transactions(
                selection="SUBSTR(time, 1, 10) as date, amount, category",
                include_categories=True,
                filter_trn_type="Expense",
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
            if trn_type == "Expense":
                df = self.db_query.get_df_with_transactions(
                    selection="SUBSTR(time, 1, 10) as date, amount",
                    filter_trn_type="Expenses",
                )
            else:
                df = self.db_query.get_df_with_transactions(
                    selection="SUBSTR(time, 1, 10) as date, amount",
                    filter_trn_type="Revenue",
                )
            date_limit = self.date.get_limit(days=30)
            df = df.loc[df["date"] > date_limit].groupby("date")["amount"].sum()

            df.plot(x="date", y="amount", kind="line")
            plt.legend(title=trn_type)
            plt.show()
