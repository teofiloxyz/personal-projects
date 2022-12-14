#!/usr/bin/python3
""" Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.
Também guarda o balanço, e é possível editá-lo."""

from Tfuncs import gmenu

from transactions import Transactions
from balance import Balance
from charts import Charts
from csvfile import CSVFile


def main() -> None:
    open_menu()


def open_menu() -> None:
    tra = Transactions()
    bal = Balance()
    cht = Charts()
    csv = CSVFile()
    title = "Fintracker-Menu"
    keys = {
        "ls": (
            lambda timespan=30: tra.show_transactions("all", timespan),
            "show past # (default 30) days transactions",
        ),
        "lse": (
            lambda timespan=30: tra.show_transactions("expenses", timespan),
            "show past # (default 30) days expenses",
        ),
        "lsr": (
            lambda timespan=30: tra.show_transactions("revenue", timespan),
            "show past # (default 30) days revenue",
        ),
        "lsb": (bal.show_balance, "show balance statement"),
        "sm": (tra.summary, "show summary"),
        "ad": (tra.add_transaction, "add transaction to database"),
        "rm": (tra.remove_transaction, "remove transaction from database"),
        "ed": (bal.edit_balance, "edit balance statement"),
        "ch": (cht.show_charts, "select and show charts"),
        "ex": (csv.export_to_csv, "export database tables to CSV file"),
    }
    extra_func = tra.opening_message
    gmenu(title, keys, extra_func)


if __name__ == "__main__":
    main()
