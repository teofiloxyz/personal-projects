#!/usr/bin/python3
"""Manages Cache(user;root;var), History(user;root),
Logs(var(contains journal)); Cleans broken symlinks(except on /run, /proc),
worthless files/folders and orphaned packages; Run this as root"""

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


class Symlinks:
    def __init__(self) -> None:
        self.utils = Utils()
        self.path_exceptions = "/run", "/proc", "/mnt"

    def manage(self) -> None:
        broken_symlinks = self.get_broken_symlinks()
        if len(broken_symlinks) == 0:
            return
        for symlink in broken_symlinks:
            if not os.path.islink(symlink) or symlink.startswith(
                self.path_exceptions
            ):
                continue
            self.remove_symlink(symlink)

    def get_broken_symlinks(self) -> list[str]:
        cmd = "find / -xtype l -print".split()
        return (
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            .stdout.decode("utf-8")
            .split("\n")
        )

    def remove_symlink(self, symlink: str) -> None:
        try:
            self.utils.remove_file(symlink)
        except PermissionError:
            return


class Trash:
    def mng_worthless_files(self) -> None:
        utils = Utils()

        files_list = "file_1", "file_2", "file_3"
        [utils.remove_file(file) for file in files_list if os.path.isfile(file)]

        folders_list = "folder_1", "folder_2", "folder_3"
        [
            utils.remove_folder(folder)
            for folder in folders_list
            if os.path.isdir(folder)
        ]

    def mng_orphaned_packs(self) -> None:
        cmd = "shell command to remove orphaned packages"
        subprocess.run(cmd, shell=True)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
