#!/usr/bin/python3

import os
import subprocess

from utils import Utils


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
