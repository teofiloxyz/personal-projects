#!/usr/bin/python3

import os

from utils import Utils


class Logs:
    def __init__(self, today: str, arcs_dir: str) -> None:
        self.today = today
        self.arcs_dir = arcs_dir
        self.utils = Utils()
        self.logs_dir = "/var/log"

    def manage(self) -> None:
        tmp_dir = self.create_tmp_folders()
        self.copy_to_tmp_folder()
        self.truncate_logs()
        self.create_logs_archive(tmp_dir)

    def create_tmp_folders(self) -> str:
        tmp_dir = f"/tmp/logs_management_{self.today}"
        self.logs_tmp_dir = f"{tmp_dir}/var"
        self.utils.create_folder(self.logs_tmp_dir)
        return tmp_dir

    def copy_to_tmp_folder(self) -> None:
        if os.listdir(self.logs_dir) != 0:
            [
                self.utils.copy_file_or_folder(
                    os.path.join(self.logs_dir, file_or_dir), self.logs_tmp_dir
                )
                for file_or_dir in os.listdir(self.logs_dir)
            ]

    def truncate_logs(self) -> None:
        [
            os.truncate(os.path.join(root_dirs_files[0], file), 0)
            for root_dirs_files in os.walk(self.logs_dir)
            for file in root_dirs_files[2]
        ]

    def create_logs_archive(self, tmp_dir: str) -> None:
        arc_dst = os.path.join(self.arcs_dir, f"Logs/{self.today}.tar.xz")
        self.utils.create_archive(tmp_dir, arc_dst)
        self.utils.remove_folder(tmp_dir)
