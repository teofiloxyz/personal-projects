#!/usr/bin/python3
""" Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.
Também guarda o balanço, e é possível editá-lo."""
# Still needs a lot of refactoring and fixing

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
            lambda timespan=30: tra.show("all", timespan),
            "show past # (default 30) days transactions",
        ),
        "lse": (
            lambda timespan=30: tra.show("expenses", timespan),
            "show past # (default 30) days expenses",
        ),
        "lsr": (
            lambda timespan=30: tra.show("revenue", timespan),
            "show past # (default 30) days revenue",
        ),
        "lsb": (bal.show, "show balance statement"),
        "sm": (tra.summary, "show summary"),
        "ad": (tra.add, "add transaction to database"),
        "rm": (tra.remove, "remove transaction from database"),
        "ed": (bal.edit, "edit balance statement"),
        "ch": (cht.show, "select and show charts"),
        "ex": (csv.export_csv, "export database transactions to CSV file"),
    }
    extra_func = tra.show_opening_message
    gmenu(title, keys, extra_func)


if __name__ == "__main__":
    main()
