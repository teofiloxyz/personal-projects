#!/usr/bin/python3
"""Manages Cache(user;root;var), History(user;root),
Logs(var(contains journal)); Cleans broken symlinks(except on /run, /proc),
worthless files/folders and orphaned packages; Run this as root"""

# could improve with inheritance (Cache, History and Logs)

from datetime import datetime

from utils import Utils

TODAY = datetime.now().strftime("%Y-%m-%d")
ARCS_DIR_PATH = "arcs_dir"


class Cache:
    def __init__(self) -> None:
        self.cache_info = {
            "user": {
                "cache_dir": Utils.get_user_path("~/.cache"),
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
        self.arcs_cache_dir = Utils.path_join(ARCS_DIR_PATH, "Cache")

    def manage(self) -> None:
        all_files = self._get_all_files()
        err = self._create_cache_archive(all_files)
        if err != 0:
            print("Error archiving cache files, not removing...")
            return
        self._remove_cache(all_files)
        self._delete_old_arcs_if_needed()

    def _get_all_files(self) -> dict[str, list]:
        all_files = {}
        for name, info in self.cache_info.items():
            dir_files = Utils.get_all_files_in_dir(info["cache_dir"])
            selected_files = [
                file for file in dir_files if file not in info["exceptions"]
            ]
            all_files[name] = selected_files
        return all_files

    def _create_cache_archive(self, all_files: dict[str, list]) -> int:
        input_paths = self._get_inputs_for_archive(all_files)
        output_path = Utils.path_join(self.arcs_cache_dir, f"{TODAY}.tar")
        return Utils.create_archive(input_paths, output_path, compress=False)

    def _get_inputs_for_archive(self, all_files: dict[str, list]) -> list:
        """Makes folder inside the achive for every type of cache dir"""

        return [
            f"--transform='s|^|{name}/|'" + file
            for name, files in all_files.items()
            for file in files
        ]

    def _remove_cache(self, all_files: dict[str, list]) -> None:
        [
            Utils.remove_file(file)
            for files in all_files.values()
            for file in files
        ]

    def _delete_old_arcs_if_needed(self) -> None:
        archives_max_mb = 4000
        while Utils.check_dir_size_mb(self.arcs_cache_dir) > archives_max_mb:
            oldest_file = Utils.get_oldest_file(self.arcs_cache_dir, ".tar")
            Utils.remove_file(oldest_file)


class History:
    def __init__(self) -> None:
        self.history_info = {
            "user": ("hist_file_1", "hist_file_2", "hist_file_3"),
            "root": ("hist_file_1", "hist_file_2", "hist_file_3"),
        }
        self.arcs_history_dir = Utils.path_join(ARCS_DIR_PATH, "History")

    def manage(self) -> None:
        err = self._create_history_archive()
        if err != 0:
            print("Error compressing history files, not removing...")
            return
        self._remove_history()

    def _create_history_archive(self) -> int:
        input_paths = self._get_inputs_for_archive()
        output_path = Utils.path_join(self.arcs_history_dir, f"{TODAY}.tar.xz")
        return Utils.create_archive(input_paths, output_path)

    def _get_inputs_for_archive(self) -> list:
        """Makes folder inside the achive for every type of hist_file"""

        return [
            f"--transform='s|^|{name}/|'" + file
            for name, files in self.history_info.items()
            for file in files
        ]

    def _remove_history(self) -> None:
        files = [file for files in self.history_info.values() for file in files]
        [Utils.remove_file(file) for file in files]


class Logs:
    def __init__(self) -> None:
        self.logs_dir = "/var/log"
        self.arcs_logs_dir = Utils.path_join(ARCS_DIR_PATH, "Logs")

    def manage(self) -> None:
        err = self._create_logs_archive()
        if err != 0:
            print("Error compressing logs, not truncating...")
            return
        self._truncate_logs()

    def _create_logs_archive(self) -> int:
        output_path = Utils.path_join(self.arcs_logs_dir, f"{TODAY}.tar.xz")
        return Utils.create_archive(self.logs_dir, output_path)

    def _truncate_logs(self) -> None:
        files = Utils.get_all_files_in_dir(self.logs_dir)
        [Utils.truncate_file(file) for file in files]


class Symlinks:
    def __init__(self) -> None:
        self.path_exceptions = "/run", "/proc", "/mnt"

    def remove(self) -> None:
        broken_symlinks = self._get_broken_symlinks()
        if len(broken_symlinks) == 0:
            return
        for symlink in broken_symlinks:
            if symlink.startswith(self.path_exceptions):
                continue
            self._remove_symlink(symlink)

    def _get_broken_symlinks(self) -> list[str]:
        cmd = "find / -xtype l -print"
        return Utils.run_cmd_and_get_output(cmd).split("\n")

    def _remove_symlink(self, symlink: str) -> None:
        try:
            Utils.remove_file(symlink)
        except PermissionError:
            return


def remove_worthless_files_and_dirs() -> None:
    files_list = "file_1", "file_2", "file_3"
    folders_list = "folder_1", "folder_2", "folder_3"
    [Utils.remove_file(file) for file in files_list]
    [Utils.remove_folder(folder) for folder in folders_list]


def remove_orphaned_packages() -> None:
    cmd = "paru --clean"  # OR "sudo pacman -Rcns $(pacman -Qdtq)"
    err = Utils.run_cmd(cmd)
    if err != 0:
        print("Error removing orphaned packages")


def main() -> None:
    Cache().manage()
    History().manage()
    Logs().manage()
    Symlinks().remove()
    remove_worthless_files_and_dirs()
    remove_orphaned_packages()


if __name__ == "__main__":
    main()
