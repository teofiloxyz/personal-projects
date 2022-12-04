#!/usr/bin/python3
"""Manager de arquivos (CLI): comprime, extrai e adiciona ao arquivo,
de forma rápida, simples e organizada"""

import argparse

from compress import Compress
from extract import Extract
from add_to_archive import AddToArchive


def main() -> None:
    compress_in, extract_in, add_in = cmd()
    if compress_in is not None:
        Compress().main(compress_in)
    elif extract_in is not None:
        Extract().main(extract_in)
    else:
        AddToArchive().main(add_in)


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
    ex_args.add_argument(
        "-a",
        "--add",
        help="add input (arg1) to archive (arg2)",
        nargs=2,
    )
    args = parser.parse_args()
    return args.compress, args.extract, args.add


if __name__ == "__main__":
    main()
