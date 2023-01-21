# CLI Menu genérico

import random
from typing import Callable
from dataclasses import dataclass


@dataclass
class Option:
    key: str
    func: Callable
    help: str


class Menu:
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

    def __init__(
        self, title: str, beginning_func: Callable | None = None
    ) -> None:
        self.title = title
        self.beginning_func = beginning_func
        self.options = dict()

    def add_option(self, key: str, func: Callable, help: str) -> None:
        if key in self.options.keys():
            raise KeyError("Key already exists...")
        self.options[key] = Option(key, func, help)

    def start(self) -> None:
        self._display_header()
        self._display_help_dialog()
        self._run_beginning_func()
        while True:
            prompt = self._get_prompt()
            if prompt == "q":
                print("Quiting...")
                return
            elif prompt in self.options.keys():
                self.options[prompt].func()
            elif prompt.replace(" ", "") != "":
                self._handle_prompt_with_args(prompt)
            else:
                self._display_help_dialog()

    def _display_header(self) -> None:
        print(self._get_header())

    def _display_help_dialog(self) -> None:
        print(self._get_help_dialog())

    def _run_beginning_func(self) -> None:
        if self.beginning_func is not None:
            print("")
            self.beginning_func()

    def _get_prompt(self) -> str:
        return input(f"{self.PROMPT_FMT}\nPick what to do -> {self.RESET}")

    def _handle_prompt_with_args(self, prompt: str) -> None:
        try:
            key, argument = prompt.split()
            self.options[key].func(argument)
        except (TypeError, IndexError, ValueError, KeyError):
            self._display_help_dialog()

    def _get_header(self) -> str:
        border = (
            (self.MENU_BORDER_1 * self.BORDER_REPS)[:-1]
            + "\n"
            + self.MENU_BORDER_2 * self.BORDER_REPS
        )
        title = "Bem-vindo ao " + self.title
        title_space = int(
            round(
                (self.BORDER_REPS * len(self.MENU_BORDER_1) - len(title)) / 2,
                0,
            )
        )
        title = " " * title_space + self.TITLE_FMT + title.upper()
        return (
            self.BORDER_FMT
            + border
            + self.RESET
            + "\n"
            + title
            + self.RESET
            + "\n"
            + self.BORDER_FMT
            + border
            + self.RESET
        )

    def _get_help_dialog(self) -> str:
        help_dialog = "\n" + self.MISC_FMT + "OPTIONS:" + self.RESET + "\n"
        for option in self.options.values():
            help_dialog += f"{option.key}: {option.help.capitalize()}\n"
        help_dialog += f"q: Quit"
        return help_dialog
