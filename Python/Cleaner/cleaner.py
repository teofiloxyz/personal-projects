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
