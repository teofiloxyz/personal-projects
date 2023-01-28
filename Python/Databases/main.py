#!/usr/bin/python3
# Menu para gerir databases

from Tfuncs import Menu

from db_manager import DBManager


def main() -> None:
    manager = DBManager()
    menu = Menu(title="Databases-Menu")

    menu.add_option(
        key="ls", func=manager.show_db_table, help="show database table"
    )
    menu.add_option(
        key="ad",
        func=manager.add_entry_to_db_table,
        help="add entry to a database table",
    )
    menu.add_option(
        key="rm",
        func=manager.remove_entry_from_db_table,
        help="remove entry from database table",
    )
    menu.add_option(
        key="dc",
        func=manager.db_table_to_csv,
        help="export database table to csv",
    )
    menu.add_option(
        key="cd",
        func=manager.csv_to_db_table,
        help="import database table from csv",
    )
    menu.add_option(
        key="adt",
        func=manager.create_db_table,
        help="create new database table",
    )
    menu.add_option(
        key="rmt", func=manager.remove_db_table, help="remove database table"
    )
    menu.add_option(
        key="add", func=manager.create_db, help="create new database"
    )
    menu.add_option(key="rmd", func=manager.remove_db, help="remove database")

    menu.start()


if __name__ == "__main__":
    main()
