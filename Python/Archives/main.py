#!/usr/bin/python3
"""Manager de arquivos (CLI): comprime e extrai,
de forma rápida, simples e organizada"""
# The whole script still needs work

import argparse

from compress import Compress
from extract import Extract


def main() -> None:
    compress_in, extract_in = cmd()
    if compress_in is not None:
        Compress().main(compress_in)
    elif extract_in is not None:
        Extract().main(extract_in)


def cmd() -> tuple:
    parser = argparse.ArgumentParser(description="Archives manager")
    ex_args = parser.add_mutually_exclusive_group()
    ex_args.add_argument(
        "-c",
        "--compress",
        help="compress input",
        nargs=1,
    )
    ex_args.add_argument(
        "-e",
        "--extract",
        help="extract input",
        nargs=1,
    )
    args = parser.parse_args()
    return args.compress, args.extract, args.add


if __name__ == "__main__":
    main()
