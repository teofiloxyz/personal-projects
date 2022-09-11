#!/usr/bin/python3
# Music-Playlist menu com diversas funções

from Tfuncs import gmenu

import argparse

from playlist import Playlist


def main() -> None:
    playlist, play = cmd()
    if play is not None:
        Playlist(playlist).play(query=" ".join(play))
    else:
        open_menu()


def cmd() -> tuple:
    parser = argparse.ArgumentParser(description="Music Playlist")
    parser.add_argument(
        "-l",
        "--playlist",
        help="playlist",
        choices=("playlist", "archive"),
        default="playlist",
    )
    ex_args = parser.add_mutually_exclusive_group()
    ex_args.add_argument(
        "-p",
        "--play",
        help="play music from playlist",
    )
    args = parser.parse_args()
    return args.playlist, args.play


def open_menu() -> None:
    pl = Playlist
    title = "Music-Playlist-Menu"
    keys = {
        "p": (lambda: pl("playlist").play(), "Play music from playlist"),
        "pa": (lambda: pl("archive").play(), "Play music from archive"),
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
