#!/usr/bin/python3
# Search tools used to incorporate in a quick launcher, like rofi-hkey

import argparse

from paths import Paths
from code import Code
from pdfs import Pdfs
from youtube import Youtube


def handle_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search tools")
    parser.add_argument(
        "command", choices=["browser", "code", "files", "pdfs", "youtube"]
    )
    parser.add_argument("query", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> None:
    args = handle_cmd_args()
    query = " ".join(args.query)

    if args.command == "browser":
        Browser().main(query)
    elif args.command == "code":
        Code().main(query)
    elif args.command == "files":
        Files().main(query)
    elif args.command == "pdfs":
        Pdf().main(query)
    elif args.command == "youtube":
        Youtube().main(query)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
