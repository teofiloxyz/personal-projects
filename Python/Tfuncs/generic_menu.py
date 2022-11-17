#!/usr/bin/python3
# CLI Menu genérico

import random


FCOL_RAND_POOL = (
    "\033[31m",  # red
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
    "\033[36m",  # cyan
    "\033[37m",  # light_gray
    "\033[90m",  # gray
    "\033[91m",  # bright_red
    "\033[92m",  # bright_green
    "\033[93m",  # bright_yellow
    "\033[94m",  # bright_blue
    "\033[95m",  # bright_magenta
    "\033[96m",  # bright_cyan
    "\033[97m",  # bright_white
)
BOLD, RESET = "\033[01m", "\033[0m"
BORDER_FMT = BOLD + random.choice(FCOL_RAND_POOL)
TITLE_FMT = BOLD + random.choice(FCOL_RAND_POOL)
MISC_FMT = BOLD + random.choice(FCOL_RAND_POOL)
PROMPT_FMT = BOLD + "\033[34m"  # blue
MENU_BORDER_1, MENU_BORDER_2, BORDER_REPS = "/\\_", "\\/ ", 28


def menu(title: str, keys: dict, extra_func=None) -> None:
    header = get_header(title)
    print(header)
    help_dialog = get_help_dialog(keys)
    print(help_dialog)

    if extra_func is not None:
        print("")
        extra_func()

    while True:
        key = input(f"{PROMPT_FMT}\nPick what to do: {RESET}")
        if key == "q":
            print("Quiting...")
            return
        elif key in keys:
            keys[key][0]()
        elif key.replace(" ", "") != "":
            if key.split()[0] in keys:
                try:
                    option, argument = key.split()
                    keys[option][0](argument)
                except (TypeError, IndexError, ValueError):
                    print(help_dialog)
            else:
                print(help_dialog)
        else:
            print(help_dialog)


def get_header(title: str) -> str:
    border = (
        (MENU_BORDER_1 * BORDER_REPS)[:-1] + "\n" + MENU_BORDER_2 * BORDER_REPS
    )
    title = "Bem-vindo ao " + title
    title_space = int(
        round(
            (BORDER_REPS * len(MENU_BORDER_1) - len(title)) / 2,
            0,
        )
    )
    title = " " * title_space + TITLE_FMT + title.upper()
    return (
        BORDER_FMT
        + border
        + RESET
        + "\n"
        + title
        + RESET
        + "\n"
        + BORDER_FMT
        + border
        + RESET
    )


def get_help_dialog(keys: dict) -> str:
    help_dialog = "\n" + MISC_FMT + "OPTIONS:" + RESET + "\n"
    for key, descriptions in keys.items():
        try:
            int(key)
            key = f"[{key}]"
        except ValueError:
            pass
        if len(descriptions) > 2:
            help_dialog += f"{key}: {descriptions[1]}\n"
            for description in descriptions[2:]:
                help_dialog += f"{key} {description}\n"
        else:
            help_dialog += f"{key}: {descriptions[1]}\n"
    help_dialog += "q: quit"
    return help_dialog
