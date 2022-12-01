#!/usr/bin/python3

import os

from utils import Utils


class History:
    def __init__(self, today: str, arcs_dir: str) -> None:
        self.today = today
        self.arcs_dir = arcs_dir
        self.utils = Utils()
        self.history_info = {
            "user": {
                "hist_files": ("hist_1", "hist_2", "hist_3"),
            },
            "root": {
                "hist_files": ("hist_1", "hist_2", "hist_3"),
            },
        }

    def manage(self) -> None:
        tmp_dir = self.create_tmp_folders()
        [
            self.move_to_tmp_folder(
                info["hist_files"],
                info["tmp_dir"],
            )
            for info in self.history_info.values()
        ]
        self.create_history_archive(tmp_dir)

    def create_tmp_folders(self) -> str:
        tmp_dir = f"/tmp/history_management_{self.today}"
        self.history_info["user"]["tmp_dir"] = f"{tmp_dir}/user"
        self.history_info["root"]["tmp_dir"] = f"{tmp_dir}/root"
        [
            self.utils.create_folder(info["tmp_dir"])
            for info in self.history_info.values()
        ]
        return tmp_dir

    def move_to_tmp_folder(self, hist_files: tuple[str], tmp_dir: str) -> None:
        [
            self.utils.move_file_or_folder(file, tmp_dir)
            for file in hist_files
            if os.path.isfile(file)
        ]

    def create_history_archive(self, tmp_dir: str) -> None:
        arc_dst = os.path.join(self.arcs_dir, f"History/{self.today}.tar.xz")
        self.utils.create_archive(tmp_dir, arc_dst)
        self.utils.remove_folder(tmp_dir)
