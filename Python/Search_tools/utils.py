#!/usr/bin/python3


class Utils:
    @staticmethod
    def divide_arg(cmd_arg: str, options: dict) -> tuple | None:
        option, entry = cmd_arg.split("", 1)
        try:
            option = options[option]
        except KeyError:
            return None
        return option, entry
