import subprocess


class Utils:
    @staticmethod
    def divide_cmd_query(cmd_query: str, options: dict) -> tuple | None:
        option, entry = cmd_query.split("", 1)
        try:
            option = options[option]
        except KeyError:
            print(
                "Error with option\n"
                f"These are the options: {' '.join(options.keys())}"
            )
            return None
        return option, entry

    @staticmethod
    def run_cmd_on_new_shell(cmd: str) -> None:
        subprocess.Popen(cmd, shell=True, start_new_session=True)
