#!/usr/bin/python3
"""Manages Cache(user;root;var), History(user;root),
Logs(var(contains journal)); Cleans broken symlinks(except on /run, /proc),
worthless files/folders and orphaned packages; Run this as root"""

import os
import subprocess
from datetime import datetime

from cache import Cache
from history import History
from logs import Logs
from symlinks import Symlinks
from utils import Utils


TODAY = datetime.now().strftime("%Y-%m-%d")
ARCS_DIR = "archives_path"


def main() -> None:
    cache, history, logs, symlinks = (
        Cache(TODAY, ARCS_DIR),
        History(TODAY, ARCS_DIR),
        Logs(TODAY, ARCS_DIR),
        Symlinks(),
    )

    cache.manage()
    history.manage()
    logs.manage()
    symlinks.manage()
    mng_worthless_files()
    mng_orphaned_packs()


def mng_worthless_files() -> None:
    utils = Utils()

    files_list = "file_1", "file_2", "file_3"
    [utils.remove_file(file) for file in files_list if os.path.isfile(file)]

    folders_list = "folder_1", "folder_2", "folder_3"
    [
        utils.remove_folder(folder)
        for folder in folders_list
        if os.path.isdir(folder)
    ]


def mng_orphaned_packs() -> None:
    cmd = "shell command to remove orphaned packages"
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()
