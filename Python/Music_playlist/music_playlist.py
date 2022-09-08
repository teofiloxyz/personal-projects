#!/usr/bin/python3
# Music-Playlist menu com diversas funções

from Tfuncs import gmenu


def main() -> None:
    open_menu()


def open_menu() -> None:
    title = "Music-Playlist-Menu"
    keys = {}
    gmenu(title, keys)


if __name__ == "__main__":
    main()
