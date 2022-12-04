#!/usr/bin/python3
# Still need refactoring

from Tfuncs import ffmt, fcol

import os
import subprocess

from utils import Utils


class Extract:
    def __init__(self) -> None:
        self.utils = Utils()
        self.arc_types = {
            ".tar.xz": "tar xvf",
            ".tar.gz": "tar xvzf",
            ".tar.bz2": "tar xvjf",
            ".tar.zst": "tar xvf",
            ".tar": "tar xvf",
            ".xz": "xz --decompress --keep --verbose",
            ".gz": "gunzip --decompress --keep --verbose",
            ".bz2": "bunzip2 --decompress --keep --verbose",
            ".zst": "zstd --decompress --keep --verbose",
            ".rar": "unrar x",
            ".tbz2": "tar xvjf",
            ".tgz": "tar xvzf",
            ".zip": "unzip",
            ".Z": "uncompress",
            ".7z": "7z x",
        }

    def main(self, input_file: str) -> None:
        input_is_entire_folder = self.utils.check_input(input_file)
        if not input_is_entire_folder:
            basename_noext, extension = self.slice_input_name(input_file)
            self.check_file_extension(input_file, extension)
            extraction_dir = self.create_extraction_dir(
                input_file, basename_noext
            )
            input_on_extraction_dir = self.move_to_extraction_dir(
                input_file, extraction_dir
            )
            self.extract_input(input_file, input_on_extraction_dir, extension)
            self.move_from_extraction_dir(input_file, input_on_extraction_dir)
            self.open_ranger_on_extraction_dir(extraction_dir)
            return

        input_files = [
            os.path.join(os.getcwd(), file)
            for file in os.listdir(os.getcwd())
            if os.path.splitext(file)[1] in self.arc_types.keys()
        ]
        for input_file in input_files:
            basename_noext, extension = self.slice_input_name(input_file)
            self.check_file_extension(input_file, extension)
            extraction_dir = self.create_extraction_dir(
                input_file, basename_noext
            )
            input_on_extraction_dir = self.move_to_extraction_dir(
                input_file, extraction_dir
            )
            self.extract_input(input_file, input_on_extraction_dir, extension)
            self.move_from_extraction_dir(input_file, input_on_extraction_dir)

    def slice_input_name(self, input_file: str) -> tuple:
        """Tem mesmo que ser assim, pq splitext separa a última ext"""

        basename = os.path.basename(input_file)
        if ".tar." in basename:
            basename, last_ext = os.path.splitext(basename)
            basename_noext, extension = os.path.splitext(basename)
            extension += last_ext
        else:
            basename_noext, extension = os.path.splitext(basename)
        return basename_noext, extension

    def check_file_extension(self, input_file: str, extension: str) -> None:
        if extension not in self.arc_types.keys():
            self.utils.error(f"Don't know how to extract '{input_file}'")

    def create_extraction_dir(
        self, input_file: str, basename_noext: str
    ) -> str:
        input_dir = os.path.dirname(input_file)
        extraction_dir = os.path.join(input_dir, "Extracted_" + basename_noext)
        while os.path.isdir(extraction_dir):
            extraction_dir += "_"

        os.mkdir(extraction_dir)
        return extraction_dir

    def move_to_extraction_dir(
        self, input_file: str, extraction_dir: str
    ) -> str:
        basename = os.path.basename(input_file)
        input_on_extraction_dir = os.path.join(extraction_dir, basename)
        os.rename(input_file, input_on_extraction_dir)
        os.chdir(extraction_dir)
        return input_on_extraction_dir

    def extract_input(
        self, input_file: str, input_on_extraction_dir: str, extension: str
    ) -> None:
        print(f"\n{ffmt.bold}{fcol.blue}Extracting {input_file}{ffmt.reset}")

        cmd = self.arc_types[extension] + " " + input_on_extraction_dir
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            self.utils.error(f"Couldn't extract {input_file}")

    def move_from_extraction_dir(
        self, input_file: str, input_on_extraction_dir: str
    ) -> None:
        os.rename(input_on_extraction_dir, input_file)
        os.chdir("..")

    def open_ranger_on_extraction_dir(self, extraction_dir: str) -> None:
        if not input(":: Open ranger on the extraction folder? [Y/n] ") in (
            "",
            "y",
            "Y",
        ):
            return

        cmd = f"alacritty -e ranger {extraction_dir}"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
