#!/usr/bin/python3
# Music-Playlist menu com diversas funções

from Tfuncs import gmenu


from playlist import Playlist


def main() -> None:
    open_menu()


def open_menu() -> None:
    pl = Playlist
    title = "Music-Playlist-Menu"
    keys = {
        "ls": (lambda: pl("playlist").show("titles"), "Show playlist titles"),
        "la": (
            lambda: pl("playlist").show("all"),
            "Show all columns from playlist",
        ),
        "lsa": (lambda: pl("archive").show("titles"), "Show archive titles"),
        "laa": (
            lambda: pl("archive").show("all"),
            "Show all columns from archive",
        ),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
