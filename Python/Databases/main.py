#!/usr/bin/python3
# Menu para editar databases
# Need a bit of tweaking and renaming

from Tfuncs import gmenu

from menu import Menu


def main() -> None:
    open_menu()


def open_menu() -> None:
    menu = Menu()
    title = "Databases-Menu"
    keys = {
        "ls": (menu.show_db_tab, "show database table"),
        "ad": (menu.add_entry_to_db_tab, "add entry to a database table"),
        "rm": (
            menu.remove_entry_from_db_tab,
            "remove entry from database table",
        ),
        "dc": (menu.db_tab_to_csv, "export database table to csv"),
        "cd": (menu.csv_to_db_tab, "import database table from csv"),
        "adt": (menu.create_db_tab, "create new database table"),
        "rmt": (menu.remove_db_tab, "remove database table"),
        "add": (menu.create_db, "create new database"),
        "rmd": (menu.remove_db, "remove database"),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
