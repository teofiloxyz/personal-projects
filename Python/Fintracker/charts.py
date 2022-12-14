#!/usr/bin/python3


class Charts:
    def show_charts(self):
        def time_chart_by_trn_type(trn_type):
            print(f"Showing {trn_type} chart...")
            df = pd.read_sql(
                "SELECT SUBSTR(time, 1, 10) as date, amount FROM "
                f'transactions WHERE trn_type = "{trn_type}"',
                self.db_con,
            )
            date_limit = datetime.strftime(
                self.now_strp - timedelta(days=30), "%Y-%m-%d"
            )
            df = df.loc[df["date"] > date_limit].groupby("date")["amount"].sum()

            df.plot(x="date", y="amount", kind="line")
            plt.legend(title=trn_type)
            plt.show()

        def pie_chart_expenses_cat():
            df = pd.read_sql(
                "SELECT SUBSTR(time, 1, 10) as date, amount, "
                "category FROM transactions LEFT JOIN expenses "
                "USING(transaction_id) WHERE "
                'trn_type = "Expense"',
                self.db_con,
            )
            date_limit = datetime.strftime(
                self.now_strp - timedelta(days=30), "%Y-%m-%d"
            )
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

        plt.style.use("dark_background")
        options = {
            "1": (
                "Revenue of last 30 days",
                lambda: time_chart_by_trn_type("Revenue"),
            ),
            "2": (
                "Expenses of last 30 days",
                lambda: time_chart_by_trn_type("Expense"),
            ),
            "3": (
                "Category percentage of expenses of last 30 days",
                pie_chart_expenses_cat,
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
