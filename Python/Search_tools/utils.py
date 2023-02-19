import os
import subprocess


class Utils:
    @staticmethod
    def run_cmd(cmd: str) -> int:
        return subprocess.call(cmd, shell=True)

    @staticmethod
    def run_cmd_on_new_shell(cmd: str) -> None:
        subprocess.Popen(cmd, shell=True, start_new_session=True)

    @staticmethod
    def run_cmd_and_get_output(cmd: str) -> str:
        return (
            subprocess.run(cmd, shell=True, capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )

    @staticmethod
    def check_if_is_dir(path: str) -> bool:
        if os.path.isdir(path):
            return True
        return False

    @staticmethod
    def get_basename(path: str) -> str:
        return os.path.basename(path)

    @staticmethod
    def get_dirname(path: str) -> str:
        return os.path.dirname(path)

    @staticmethod
    def get_modification_time(path: str) -> float:
        return os.path.getmtime(path)
