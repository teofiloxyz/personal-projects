#!/usr/bin/python3
"""Manages Cache(user;root;var), History(user;root),
Logs(var(contains journal)); Cleans broken symlinks(except on /run, /proc),
worthless files/folders and orphaned packages; Run this as root"""

import os
import shutil
import subprocess
from datetime import datetime


class Cleaner:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.arcs_dir = "archives_path"

    def main(self):
        self.mng_cache()
        self.mng_history()
        self.mng_logs()
        self.mng_symlinks()
        self.mng_worthless_files()
        self.mng_pac_orphans()

    @staticmethod
    def move_file_or_folder(file_or_folder, destination):
        shutil.move(file_or_folder, destination)

    @staticmethod
    def copy_file_or_folder(file_or_folder, destination):
        if os.path.isdir(file_or_folder):
            shutil.copytree(file_or_folder, destination, dirs_exist_ok=True)
        else:
            if os.path.isdir(destination):
                destination = os.path.join(
                    destination, os.path.basename(file_or_folder)
                )
            shutil.copyfile(file_or_folder, destination)

    @staticmethod
    def remove_file(file):
        os.remove(file)

    @staticmethod
    def remove_folder(folder):
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def create_folder(folder):
        os.makedirs(folder, exist_ok=True)

    @staticmethod
    def create_archive(input_dir, output, compress=True):
        cp = " --use-compress-program='xz -9T0'" if compress is True else ""
        subprocess.run(f"tar cf {output}{cp} -C {input_dir} .", shell=True)

    @staticmethod
    def check_dir_size_mb(input_dir):
        size = subprocess.run(
            ["du", "-m", input_dir], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        return int(size.split()[0])

    @staticmethod
    def get_oldest_file(input_dir, extension, reverse=False):
        files = {
            os.path.getmtime(os.path.join(input_dir, file)): os.path.join(
                input_dir, file
            )
            for file in os.listdir(input_dir)
            if file.endswith(extension)
        }

        if reverse is False:
            return files[min(files.keys())]
        return files[max(files.keys())]

    def mng_cache(self):
        user_cache, root_cache, var_cache = (
            os.path.expanduser("~/.cache"),
            "/root/.cache",
            "/var/cache",
        )
        user_cache_excp = "exception_1", "exception_2", "exception_3"
        root_cache_excp = "exception_1", "exception_2", "exception_3"
        var_cache_excp = "exception_1", "exception_2", "exception_3"

        tmp_dir = f"/tmp/cache_management_{self.today}"
        tmp_user, tmp_root, tmp_var = (
            f"{tmp_dir}/user_cache",
            f"{tmp_dir}/root_cache",
            f"{tmp_dir}/var_cache",
        )
        self.create_folder(" ".join([tmp_user, tmp_root, tmp_var]))

        if os.listdir(user_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(user_cache, file_dir), tmp_user
                )
                for file_dir in os.listdir(user_cache)
                if file_dir not in user_cache_excp
            ]

        if os.listdir(root_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(root_cache, file_dir), tmp_root
                )
                for file_dir in os.listdir(root_cache)
                if file_dir not in root_cache_excp
            ]

        if os.listdir(var_cache) != 0:
            [
                self.move_file_or_folder(
                    os.path.join(var_cache, file_dir), tmp_var
                )
                for file_dir in os.listdir(var_cache)
                if file_dir not in var_cache_excp
            ]

        arc_dst = os.path.join(self.arcs_dir, f"Cache/{self.today}.tar")
        # Não é necessário compressão pq não fará grande diferença em cache
        self.create_archive(tmp_dir, arc_dst, compress=False)
        self.remove_folder(tmp_dir)

        archives_max_mb = int("<number>")
        while self.check_dir_size_mb(self.arcs_dir) > archives_max_mb:
            self.remove_file(self.get_oldest_file(self.arcs_dir, ".tar"))

    def mng_history(self):
        user_hist_list = "hist_1", "hist_2", "hist_3"
        root_hist_list = "hist_1", "hist_2", "hist_3"

        tmp_dir = f"/tmp/history_management_{self.today}"
        tmp_user, tmp_root = f"{tmp_dir}/user", f"{tmp_dir}/root"
        self.create_folder(" ".join([tmp_user, tmp_root]))

        [
            self.move_file_or_folder(file, tmp_user)
            for file in user_hist_list
            if os.path.isfile(file)
        ]

        [
            self.move_file_or_folder(file, tmp_root)
            for file in root_hist_list
            if os.path.isfile(file)
        ]

        arc_dst = os.path.join(self.arcs_dir, f"History/{self.today}.tar.xz")
        self.create_archive(tmp_dir, arc_dst)
        self.remove_folder(tmp_dir)

    def mng_logs(self):
        # Log files get copied and truncated
        var_logs = "/var/log"

        tmp_dir = f"/tmp/logs_management_{self.today}"
        tmp_var = f"{tmp_dir}/var"
        self.create_folder(tmp_var)

        if os.listdir(var_logs) != 0:
            [
                self.copy_file_or_folder(
                    os.path.join(var_logs, file_dir), tmp_var
                )
                for file_dir in os.listdir(var_logs)
            ]
            [
                os.truncate(os.path.join(root_dirs_files[0], file), 0)
                for root_dirs_files in os.walk(var_logs)
                for file in root_dirs_files[2]
            ]

        arc_dst = os.path.join(self.arcs_dir, f"Logs/{self.today}.tar.xz")
        self.create_archive(tmp_dir, arc_dst)
        self.remove_folder(tmp_dir)

    def mng_symlinks(self):
        cmd = "find / -xtype l -print".split()
        broken_slinks_list = (
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        if len(broken_slinks_list) == 0:
            return

        for link in broken_slinks_list:
            if not os.path.islink(link):
                continue
            if (
                link.startswith("/run")
                or link.startswith("/proc")
                or link.startswith("/mnt")
            ):
                continue
            try:
                self.remove_file(link)
            except PermissionError:
                continue

    def mng_worthless_files(self):
        files_list = "file_1", "file_2", "file_3"
        folders_list = "folder_1", "folder_2", "folder_3"

        for file in files_list:
            if not os.path.isfile(file):
                continue
            self.remove_file(file)

        for folder in folders_list:
            if not os.path.isdir(folder):
                continue
            self.remove_folder(folder)

    def mng_pac_orphans(self):
        cmd = "shell command"
        subprocess.run(cmd, shell=True)


Cleaner().main()
