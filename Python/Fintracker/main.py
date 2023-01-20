#!/usr/bin/python3
""" Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.
Também guarda o balanço, e é possível editá-lo."""
# Still needs some refactoring

from Tfuncs import Menu

from transactions import Transactions, TransactionType, Charts
from balance import Balance


def main() -> None:
    transactions, balance, charts = Transactions(), Balance(), Charts()
    menu = Menu(
        title="Fintracker-Menu", beginning_func=transactions.show_summary
    )

    menu.add_option(
        key="ls",
        func=lambda timespan=30: transactions.show(timespan),
        help="show past # (default 30) days transactions",
    )
    menu.add_option(
        key="lse",
        func=lambda timespan=30: transactions.show(
            timespan, TransactionType.EXPENSE
        ),
        help="show past # (default 30) days expenses",
    )
    menu.add_option(
        key="lsr",
        func=lambda timespan=30: transactions.show(
            timespan, TransactionType.REVENUE
        ),
        help="show past # (default 30) days revenue",
    )
    menu.add_option(
        key="lsb",
        func=lambda timespan=30: transactions.show(
            timespan, TransactionType.BALANCE
        ),
        help="show past # (default 30) days balance editions",
    )
    menu.add_option(key="b", func=balance.show, help="show balance statement")
    menu.add_option(
        key="sm",
        func=transactions.show_summary,
        help="show transactions summary",
    )
    menu.add_option(
        key="ad", func=transactions.add, help="add transaction to database"
    )
    menu.add_option(
        key="rm",
        func=transactions.remove,
        help="remove transaction from database",
    )
    menu.add_option(key="ed", func=balance.edit, help="edit balance statement")
    menu.add_option(key="ch", func=charts.show, help="select and show charts")
    menu.add_option(
        key="ex",
        func=transactions.export_to_csv,
        help="export database transactions to CSV file",
    )

    menu.start()


if __name__ == "__main__":
    main()
