#!/usr/bin/python3
# CLI Mounting tool for partitions

import argparse

from mount import Mount
from dismount import Dismount


def handle_cmd_args() -> tuple:
    parser = argparse.ArgumentParser(description="Mounting tool")
    ex_args = parser.add_mutually_exclusive_group()
    ex_args.add_argument(
        "-m",
        "--mount",
        action="store_true",
        help="mount a sdev/partition",
    )
    ex_args.add_argument(
        "-d",
        "--dismount",
        action="store_true",
        help="dismount a sdev/partition",
    )
    args = parser.parse_args()
    return args.mount, args.dismount


def main() -> None:
    mount, dismount = handle_cmd_args()
    if mount:
        Mount().main()
    elif dismount:
        Dismount().main()
    else:
        print("Either --mount or --dismount...")


if __name__ == "__main__":
    main()
