import numpy as np
import matplotlib.pyplot as plt

from utils import Date
from database import Query


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
