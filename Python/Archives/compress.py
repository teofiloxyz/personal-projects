#!/usr/bin/python3
# Needs tweaking and testing

import os
import subprocess

from utils import Utils


class Compress:
    def __init__(self) -> None:
        self.utils = Utils()
        self.methods_file = {
            "1": (
                "xz(max)",
                ".xz",
                "xz -9kT0 input --stdout > output",
            ),
            "2": (
                "xz(med)",
                ".xz",
                "xz -6kT0 input --stdout > output",
            ),
            "3": (
                "zip",
                ".zip",
                "zip --junk-paths output input",
            ),
            "4": (
                "7zip",
                ".7z",
                (
                    "7z a output -mhe=on input -p",
                    "7z a output input",
                ),
            ),
        }
        self.methods_folder = {
            "1": (
                "tar.xz(max)",
                ".tar.xz",
                "tar cvf output --use-compress-program='xz -9T0' input",
            ),
            "2": (
                "tar",
                ".tar",
                "tar cvf output input",
            ),
            "3": ("zip", ".zip", "zip output input"),
            "4": (
                "7zip",
                ".7z",
                (
                    "7z a output -mhe=on input -p",
                    "7z a output input",
                ),
            ),
            "5": (
                "tar.xz(med)",
                ".tar.xz",
                "tar cvf output --use-compress-program='xz -6T0' input",
            ),
        }

    def main(self, input_file_or_dir: str) -> None:
        input_is_entire_folder = self.utils.check_input(input_file_or_dir)
        if input_is_entire_folder:
            input_file_or_dir = "."
        compression_method = self.get_compression_method(input_is_entire_folder)
        output = self.get_output_name(
            input_file_or_dir, input_is_entire_folder, compression_method
        )
        self.compress_input(input_file_or_dir, output, compression_method)

    def get_compression_method(self, input_is_entire_folder: bool) -> tuple:
        compression_methods = (
            self.methods_folder if input_is_entire_folder else self.methods_file
        )

        prompt = input(
            "\n".join(
                f"[{key}] {val[0]}" for key, val in compression_methods.items()
            )
            + "\nChoose the compression method: "
        )
        try:
            return compression_methods[prompt]
        except KeyError:
            self.utils.error("Aborted...")

    def get_output_name(
        self,
        input_file_or_dir: str,
        input_is_entire_folder: bool,
        compression_method: tuple,
    ) -> str:
        extension = compression_method[1]
        if input_is_entire_folder:
            output_name = os.path.basename(os.getcwd()) + extension
        else:
            output_name = os.path.basename(input_file_or_dir) + extension

        while os.path.isfile(output_name):
            output_name = "_" + output_name
        return output_name

    def compress_input(
        self, input_file_or_dir: str, output: str, compression_method: tuple
    ) -> None:
        if compression_method[0] == "7zip":
            if input(":: Want encryption? You should! [Y/n] ") in (
                "",
                "y",
                "Y",
            ):
                cmd = compression_method[2][0]
            else:
                cmd = compression_method[2][1]
        else:
            cmd = compression_method[2]

        cmd = cmd.replace("input", input_file_or_dir)
        cmd = cmd.replace("output", output)

        err = subprocess.call(cmd, shell=True)
        if err != 0:
            self.utils.error(f"Coudn't compress {input_file_or_dir}")
