#!/usr/bin/python3
"""Manager de arquivos (CLI): comprime e extrai,
de forma rápida, simples e organizada"""

import os
import argparse

from compress import Compress
from extract import Extract


def handle_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archives manager")
    ex_args = parser.add_mutually_exclusive_group(required=True)
    ex_args.add_argument(
        "-c",
        "--compress",
        help="compress input",
        nargs=argparse.REMAINDER,
    )
    ex_args.add_argument(
        "-e",
        "--extract",
        help="extract input",
        nargs=argparse.REMAINDER,
    )
    return parser.parse_args()


def get_all_files_including_hidden() -> list[str]:
    return [file for file in os.listdir()]


def main() -> None:
    args = handle_cmd_args()
    input_files = args.compress or args.extract
    if input_files == ["."]:
        input_files = get_all_files_including_hidden()

    if args.compress:
        Compress(input_files).main()
    elif args.extract:
        Extract(input_files).main()


if __name__ == "__main__":
    main()
