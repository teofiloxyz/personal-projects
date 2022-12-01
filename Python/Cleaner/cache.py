#!/usr/bin/python3

import os

from utils import Utils


class Cache:
    def __init__(self, today: str, arcs_dir: str) -> None:
        self.today = today
        self.arcs_dir = arcs_dir
        self.utils = Utils()
        self.cache_info = {
            "user": {
                "cache_dir": os.path.expanduser("~/.cache"),
                "exceptions": ("exception_1", "exception_2", "exception_3"),
            },
            "root": {
                "cache_dir": "/root/.cache",
                "exceptions": ("exception_1", "exception_2", "exception_3"),
            },
            "var": {
                "cache_dir": "/var/cache",
                "exceptions": ("exception_1", "exception_2", "exception_3"),
            },
        }

    def manage(self) -> None:
        tmp_dir = self.create_tmp_folders()
        [
            self.move_to_tmp_folder(
                info["cache_dir"], info["tmp_dir"], info["exceptions"]
            )
            for info in self.cache_info.values()
        ]
        self.create_cache_archive(tmp_dir)
        self.delete_old_arcs_if_needed()

    def create_tmp_folders(self) -> str:
        tmp_dir = f"/tmp/cache_management_{self.today}"
        self.cache_info["user"]["tmp_dir"] = f"{tmp_dir}/user_cache"
        self.cache_info["root"]["tmp_dir"] = f"{tmp_dir}/root_cache"
        self.cache_info["var"]["tmp_dir"] = f"{tmp_dir}/var_cache"

        [
            self.utils.create_folder(info["tmp_dir"])
            for info in self.cache_info.values()
        ]
        return tmp_dir

    def move_to_tmp_folder(
        self, cache_dir: str, tmp_dir: str, cache_exceptions: tuple[str]
    ) -> None:
        if os.listdir(cache_dir) != 0:
            [
                self.utils.move_file_or_folder(
                    os.path.join(cache_dir, file_or_dir), tmp_dir
                )
                for file_or_dir in os.listdir(cache_dir)
                if file_or_dir not in cache_exceptions
            ]

    def create_cache_archive(self, tmp_dir: str) -> None:
        arc_dst = os.path.join(self.arcs_dir, f"Cache/{self.today}.tar")

        # Ñ é necessário compressão pq ñ fará grande diferença em cache files
        self.utils.create_archive(tmp_dir, arc_dst, compress=False)
        self.utils.remove_folder(tmp_dir)

    def delete_old_arcs_if_needed(self) -> None:
        archives_max_mb = int("<number>")
        while self.utils.check_dir_size_mb(self.arcs_dir) > archives_max_mb:
            oldest_file = self.utils.get_oldest_file(self.arcs_dir, ".tar")
            self.utils.remove_file(oldest_file)
