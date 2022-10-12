#!/usr/bin/python3
# Search a definition of a word

from Tfuncs import rofi

import argparse

from en_dictionary import EnDictionary
from pt_dictionary import PtDictionary


def main() -> None:
    lang_funcs = {"english": EnDictionary, "portuguese": PtDictionary}
    language, entry = cmd()
    while True:
        result = lang_funcs[language]().search(entry)
        prompt = "Enter another entry to search its definition, or [q]uit: "
        entry = rofi.simple_prompt(prompt, message=result)
        if entry == "q":
            return


def cmd() -> tuple:
    parser = argparse.ArgumentParser(description="Dictionaries")
    parser.add_argument(
        "-l",
        "--language",
        help="dictionary language",
        choices=("english", "portuguese"),
        default="english",
    )
    parser.add_argument(
        "entry",
        help="entry to search definition",
        nargs="*",
    )
    args = parser.parse_args()
    return args.language, " ".join(args.entry)


if __name__ == "__main__":
    main()
