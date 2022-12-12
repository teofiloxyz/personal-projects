#!/usr/bin/python3
# Search tools used to incorporate in a quick launcher, like rofi-hkey

import argparse

from browser import Browser
from code import Code
from files import Files
from pdf import Pdf
from youtube import Youtube


def main() -> None:
    browser, code, files, pdfs, youtube = cmd()
    if browser is not None:
        Browser().main(browser)
    elif code is not None:
        Code().main(code)
    elif files is not None:
        Files().main(files)
    elif pdfs is not None:
        Pdf().main(pdfs)
    elif youtube is not None:
        Youtube().main(youtube)


def cmd() -> tuple:
    parser = argparse.ArgumentParser(description="Search tools")
    ex_args = parser.add_mutually_exclusive_group()
    ex_args.add_argument(
        "-b",
        "--browser",
        help="search on browser",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-c",
        "--code",
        help="search within code",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-f",
        "--files",
        help="search file names",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-p",
        "--pdfs",
        help="search within pdf files",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-y",
        "--youtube",
        help="search on youtube",
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()
    return (
        args.browser,
        args.code,
        args.files,
        args.pdfs,
        args.youtube,
    )


if __name__ == "__main__":
    main()
