#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from utils import Utils
from database import Database


class Charts:
    utils = Utils()
    database = Database()

    def show(self) -> None:
        plt.style.use("dark_background")
        options = {
            "1": (
                "Revenue of last 30 days",
                lambda: self.show_time_chart_by_trn_type("Revenue"),
            ),
            "2": (
                "Expenses of last 30 days",
                lambda: self.show_time_chart_by_trn_type("Expense"),
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
        df = self.database.Query().create_df_of_expenses()
        date_limit = self.utils.get_date_limit(days=30)
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
        df = self.database.Query().create_df_trn_type(trn_type)
        date_limit = self.utils.get_date_limit(days=30)
        df = df.loc[df["date"] > date_limit].groupby("date")["amount"].sum()

        df.plot(x="date", y="amount", kind="line")
        plt.legend(title=trn_type)
        plt.show()
