#!/usr/bin/python3
# Music-Playlist menu com diversas funções

from Tfuncs import Menu

import argparse

from playlist import Playlist
from youtube import Youtube
from csvfile import CSVFile


def handle_cmd_args() -> argparse.Namespace:
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
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument("-a", "--add", help="add music to playlist")
    return parser.parse_args()


def open_menu() -> None:
    pl = Playlist
    menu = Menu(title="Music-Playlist-Menu")

    menu.add_option(
        key="p",
        func=lambda: pl("playlist").play(),
        help="Play music from playlist",
    )
    menu.add_option(
        key="pa",
        func=lambda: pl("archive").play(),
        help="Play music from archive",
    )
    menu.add_option(
        key="ad",
        func=lambda: pl("playlist").add(),
        help="Add music to playlist",
    )
    menu.add_option(
        key="rm",
        func=lambda: pl("playlist").remove(),
        help="Remove music from playlist that goes to archive",
    )
    menu.add_option(
        key="ada", func=lambda: pl("archive").add(), help="Add music to archive"
    )
    menu.add_option(
        key="rma",
        func=lambda: pl("archive").remove(),
        help="Remove music from archive",
    )
    menu.add_option(
        key="rc",
        func=lambda: pl("archive").recover_arc(),
        help="Recover music from archive",
    )
    menu.add_option(
        key="ed",
        func=lambda: pl("playlist").edit_entry(),
        help="Edit title or genre of a music from playlist",
    )
    menu.add_option(
        key="eda",
        func=lambda: pl("archive").edit_entry(),
        help="Edit title or genre of a music from archive",
    )
    menu.add_option(
        key="ls",
        func=lambda: pl("playlist").show("titles"),
        help="Show playlist titles",
    )
    menu.add_option(
        key="la",
        func=lambda: pl("playlist").show("all"),
        help="Show all columns from playlist",
    )
    menu.add_option(
        key="lsa",
        func=lambda: pl("archive").show("titles"),
        help="Show archive titles",
    )
    menu.add_option(
        key="laa",
        func=lambda: pl("archive").show("all"),
        help="Show all columns from archive",
    )
    menu.add_option(
        key="d",
        func=lambda: Youtube().download_from_txt(),
        help="Download from txt file with titles and/or links",
    )
    menu.add_option(
        key="xc",
        func=lambda: CSVFile().export_csv(),
        help="Export playlist (or archive) to CSV",
    )
    menu.add_option(
        key="ic",
        func=lambda: CSVFile().import_csv(),
        help="Import playlist (or archive) from CSV",
    )

    menu.start()


def main() -> None:
    args = handle_cmd_args()
    if not args.play:
        Playlist(args.playlist).play(query=" ".join(args.play))
    elif not args.add:
        Playlist(args.playlist).add(ytb_code=args.add)
    else:
        open_menu()


if __name__ == "__main__":
    main()
