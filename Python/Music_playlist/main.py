#!/usr/bin/python3
# Music-Playlist menu com diversas funções

from Tfuncs import Menu

import argparse

from playlist import Playlist, PlaylistType
from youtube import Youtube


def handle_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Music Playlist")
    parser.add_argument(
        "-l",
        "--playlist",
        help="playlist",
        choices=("active", "archive"),
        default="active",
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
    active = Playlist(PlaylistType.ACTIVE)
    archive = Playlist(PlaylistType.ARCHIVE)
    menu = Menu(title="Music-Playlist-Menu")

    menu.add_option(
        key="p",
        func=active.play,
        help="Play music from active playlist",
    )
    menu.add_option(
        key="pa",
        func=archive.play,
        help="Play music from archive",
    )
    menu.add_option(
        key="ad",
        func=active.add,
        help="Add music to active playlist",
    )
    menu.add_option(
        key="rm",
        func=active.remove,
        help="Remove music from active playlist that goes to archive",
    )
    menu.add_option(
        key="ada",
        func=archive.add,
        help="Add music to archive",
    )
    menu.add_option(
        key="rma",
        func=archive.remove,
        help="Remove music from archive",
    )
    menu.add_option(
        key="rc",
        func=archive.recover_arc,
        help="Recover music from archive",
    )
    menu.add_option(
        key="ed",
        func=active.edit_entry,
        help="Edit title or genre of a music from active playlist",
    )
    menu.add_option(
        key="eda",
        func=archive.edit_entry,
        help="Edit title or genre of a music from archive",
    )
    menu.add_option(
        key="ls",
        func=lambda: active.show("titles"),
        help="Show active playlist titles",
    )
    menu.add_option(
        key="la",
        func=lambda: active.show("all"),
        help="Show all columns from active playlist",
    )
    menu.add_option(
        key="lsa",
        func=lambda: archive.show("titles"),
        help="Show archive titles",
    )
    menu.add_option(
        key="laa",
        func=lambda: archive.show("all"),
        help="Show all columns from archive",
    )
    menu.add_option(
        key="xc",
        func=active.export_to_csv_file,
        help="Export playlist to CSV",
    )
    menu.add_option(
        key="d",
        func=Youtube().download_from_txt,
        help="Download from txt file with titles and/or links",
    )

    menu.start()


def main() -> None:
    args = handle_cmd_args()
    if args.playlist == "active":
        playlist = PlaylistType.ACTIVE
    else:
        playlist = PlaylistType.ARCHIVE

    if args.play:
        Playlist(playlist).play(query=" ".join(args.play))
    elif args.add:
        Playlist(playlist).add(ytb_code=args.add)
    else:
        open_menu()


if __name__ == "__main__":
    main()
