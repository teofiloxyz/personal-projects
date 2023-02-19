#!/usr/bin/python3
# Search tools used to incorporate in a quick launcher, like rofi-hkey

import argparse

from paths import Paths
from notes import Notes
from code import Code
from pdfs import Pdfs
from youtube import Youtube


def handle_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search tools")
    parser.add_argument(
        "-t", "--type", choices=("paths", "notes", "code", "pdfs", "youtube")
    )
    parser.add_argument("-p", "--search-path", default="/home")
    parser.add_argument("-q", "--query", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> None:
    args = handle_cmd_args()
    search_type = args.type
    search_path = args.search_path
    query = args.query
    if not search_type or not query:
        print("Invalid command")
        return
    query = " ".join(args.query)

    if search_type == "paths":
        Paths(search_path).search(query)
    elif search_type == "notes":
        Notes(search_path).search(query)
    elif search_type == "code":
        Code(search_path).search(query)
    elif search_type == "pdfs":
        Pdfs(search_path).search(query)
    elif search_type == "youtube":
        Youtube().search(query)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
