#!/usr/bin/python3
"""Manager de arquivos (CLI): comprime, descomprime e adiciona ao arquivo,
de forma rápida, simples e organizada"""

import os
import sys
import shutil
import subprocess
from configparser import ConfigParser
from Tfuncs import oupt, qst, ffmt, fcol


class Archives:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.terminal = self.config["GENERAL"]["terminal"]
        self.rej_sound = self.config["GENERAL"]["rejected_sound"]

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

    def main(self):
        self.check_option()
        self.check_input()
        if self.option == "add":
            self.check_input2()
        self.process()

    def error(self, msg):
        subprocess.Popen(["paplay", self.rej_sound], start_new_session=True)
        print("Error: " + msg)
        exit(1)

    def check_option(self):
        self.opst_dict = {
            "extract": self.extract,
            "compress": self.compress,
            "add": self.add_to_archive,
        }
        try:
            self.option = sys.argv[1]
        except IndexError:
            self.error("Command needs options (extract, compress or add)")

        if self.option in self.opst_dict.keys():
            self.process = self.opst_dict[self.option]
        else:
            self.error(
                "First argument needs to be 'extract', " "'compress' or 'add'"
            )

    def check_input(self):
        try:
            self.input = sys.argv[2]
        except IndexError:
            if self.option == "add":
                self.error("Command needs an input...")
            self.input = ""

        self.entire_folder = (
            True
            if self.option != "add" and self.input in ("", "all", "a", "al")
            else False
        )
        if not self.entire_folder:
            self.input = os.path.join(os.getcwd(), self.input)
            if self.input[-1] == "/":
                self.input = self.input[:-1]
        else:
            self.input = os.getcwd() + "/"

    def check_input2(self):
        # Apenas é usado com a opção add
        try:
            self.input2 = os.path.join(os.getcwd(), sys.argv[3])
        except IndexError:
            self.error("Command needs a second input to add the 1st input...")

        if not os.path.exists(self.input2):
            self.error(f"'{self.input2}' does not exist...")

        extension = os.path.splitext(self.input2)[1]
        if extension not in self.arc_types.keys():
            self.error(
                f"'{self.input2}' is not a recognized archive " "format..."
            )

    def extract(self):
        def extraction_process(self):
            get_arc_name(self)
            check_arc_extension(self)
            create_extracted_dir(self)
            move_to_extracted_dir(self)
            extract_archive(self)
            move_from_extracted_dir(self)

        def get_arc_name(self):
            if not os.path.exists(self.input):
                self.error(f"'{self.input}' does not exist...")
            self.basename = os.path.basename(self.input)

            if ".tar." in self.basename:
                name, self.extension = os.path.splitext(self.basename)
                self.name, ex2 = os.path.splitext(name)
                if ex2 == ".tar":
                    self.extension = ex2 + self.extension
            else:
                self.name, self.extension = os.path.splitext(self.basename)

        def check_arc_extension(self):
            if self.extension not in self.arc_types.keys():
                self.error(f"Don't know how to extract '{self.input}'")

        def create_extracted_dir(self):
            input_dir = os.path.dirname(self.input)
            self.extracted_dir = os.path.join(
                input_dir, "Extracted_" + self.name
            )

            while os.path.isdir(self.extracted_dir):
                extracted_dir_name = os.path.basename(self.extracted_dir)
                n = extracted_dir_name.split("Extracted_")[0]
                if n == "":
                    self.extracted_dir = os.path.join(
                        input_dir, "2Extracted_" + self.name
                    )
                else:
                    self.extracted_dir = os.path.join(
                        input_dir, str(int(n) + 1) + "Extracted_" + self.name
                    )

            os.mkdir(self.extracted_dir)

        def move_to_extracted_dir(self):
            self.input_on_extracted_dir = os.path.join(
                self.extracted_dir, self.basename
            )
            os.rename(self.input, self.input_on_extracted_dir)
            os.chdir(self.extracted_dir)

        def extract_archive(self):
            print(
                f"\n{ffmt.bold}{fcol.blue}Extracting "
                f"{self.input}{ffmt.reset}"
            )
            cmd = (
                self.arc_types[self.extension]
                + " "
                + self.input_on_extracted_dir
            )
            subprocess.run(cmd, shell=True)

        def move_from_extracted_dir(self):
            os.rename(self.input_on_extracted_dir, self.input)
            os.chdir("..")

        def open_ranger_on_extracted_dir(self):
            if not input(
                ":: Do you want to open ranger on the extraction "
                "folder? [Y/n] "
            ) in ("", "y", "Y"):
                return

            cmd = f"{self.terminal} -e ranger {self.extracted_dir}"
            subprocess.Popen(cmd, shell=True, start_new_session=True)

        if self.entire_folder:
            # Extrai todos os archivos da pasta
            arcs_list = [
                os.path.join(os.getcwd(), file)
                for file in os.listdir(os.getcwd())
                if os.path.splitext(file)[1] in self.arc_types.keys()
            ]

            for arc in arcs_list:
                self.input = arc
                extraction_process(self)

        else:
            extraction_process(self)
            open_ranger_on_extracted_dir(self)

    def compress(self):
        def compress_process(self):
            get_compression_method(self)
            check_output_name(self)
            compress_input(self)

        def name_output(self):
            self.output = oupt.files(
                question="Enter the output full path, or "
                "just the name for same input dir, or leave "
                "empty for same as input\n: ",
                file_input=self.input,
                output_name_change=True,
            )

        def get_compression_method(self):
            # Ou apenas um ficheiro é comprimido, ou uma pasta inteira
            if os.path.isfile(self.input):
                methods = {
                    "1": (
                        "xz(max)",
                        "xz",
                        f"xz -9kT0 {self.input} "
                        f"--stdout > {self.output}.xz",
                    ),
                    "2": (
                        "xz(med)",
                        "xz",
                        f"xz -6kT0 {self.input} "
                        f"--stdout > {self.output}.xz",
                    ),
                    "3": (
                        "gz",
                        "gz",
                        f"gzip {self.input} --stdout > {self.output}.gz",
                    ),
                    "4": (
                        "7zip",
                        "7z",
                        (
                            f"7z a {self.output}.7z -mhe=on {self.input} -p",
                            f"7z a {self.output}.7z {self.input}",
                        ),
                    ),
                }
            else:
                self.entire_folder = True
                self.input_folder = self.input
                input_folder_contents = os.listdir(self.input_folder)
                self.input = "*"

                # Ver se há algum hidden file na pasta
                for content in input_folder_contents:
                    if content[0] == ".":
                        self.input = "."
                        break

                if os.path.basename(self.output).split(".")[0] == "":
                    self.output += os.path.dirname(self.input_folder).split(
                        "/"
                    )[-1]
                methods = {
                    "1": (
                        "tar.xz(max)",
                        "tar.xz",
                        f"tar cvf {self.output}.tar.xz "
                        f"--use-compress-program='xz -9T0' {self.input}",
                    ),
                    "2": (
                        "tar.xz(med)",
                        "tar.xz",
                        f"tar cvf {self.output}.tar.xz "
                        f"--use-compress-program='xz -6T0' {self.input}",
                    ),
                    "3": (
                        "tar.gz",
                        "tar.gz",
                        f"tar cvzf {self.output}.tar.gz {self.input}",
                    ),
                    "4": (
                        "7zip",
                        "7z",
                        (
                            f"7z a {self.output}.7z -mhe=on {self.input} -p",
                            f"7z a {self.output}.7z {self.input}",
                        ),
                    ),
                    "5": (
                        "tar",
                        "tar",
                        f"tar cvf {self.output}.tar {self.input}",
                    ),
                }

            if self.option == "add":
                # Caso a opção seja add, o método é detetado
                self.method = None
                methods = list(methods.values())
                for method in methods:
                    if method[1] == self.extension[1:]:
                        self.method = method
                        break

                if self.method is None:
                    self.error("Archive extension not supported, sorry...")
            else:
                question = (
                    "\n".join(
                        f"[{key}] {val[0]}" for key, val in methods.items()
                    )
                    + "\nChoose compressing method: "
                )
                self.method = qst.opts(question, methods)
                if self.method == "q":
                    self.error("Aborted...")

        def check_output_name(self):
            output_name = self.output + "." + self.method[1]
            while os.path.exists(output_name):
                output_dirname = os.path.dirname(output_name)
                output_basename = os.path.basename(output_name)
                output_name = output_dirname + "_" + output_basename

        def compress_input(self):
            if self.method[1] == "7z":
                if input(":: Want encryption? You should! " "[Y/n] ") in (
                    "",
                    "y",
                    "Y",
                ):
                    cmd = self.method[2][0]
                else:
                    cmd = self.method[2][1]
            else:
                cmd = self.method[2]

            if self.entire_folder:
                current_dir = os.getcwd()
                os.chdir(self.input_folder)
                subprocess.run(cmd, shell=True)
                os.chdir(current_dir)
            else:
                subprocess.run(cmd, shell=True)

        if self.option == "add":
            # self.name vem da função extract
            self.output = os.path.join(os.getcwd(), self.name + "_new")
            compress_process(self)
        else:
            name_output(self)
            compress_process(self)

    def add_to_archive(self):
        def extract_arc(self):
            self.input_to_add = self.input
            self.input = self.input2
            self.extract()

        def navigate_in_extracted(self):
            def get_current_dir_folders():
                return [
                    os.path.join(current_dir, entry)
                    for entry in os.listdir(current_dir)
                    if os.path.isdir(os.path.join(current_dir, entry))
                ]

            # self.extracted_dir vem da função extract
            current_dir = self.extracted_dir
            current_dir_folders = get_current_dir_folders()
            while len(current_dir_folders) != 0:
                print("\nFound folders inside:")
                for n, folder in enumerate(current_dir_folders, 1):
                    print(f"[{n}] {folder}")

                next_dir = input(
                    "Pick the number of folder to open, or leave "
                    "empty to put the input in current dir: "
                )
                if next_dir == "":
                    break
                current_dir = current_dir_folders[int(next_dir) - 1]
                current_dir_folders = get_current_dir_folders()

            self.current_dir = current_dir

        def copy_input_to_extracted(self):
            arc_dst_dir = self.current_dir
            arc_dst = os.path.join(
                arc_dst_dir, os.path.basename(self.input_to_add)
            )
            if os.path.exists(arc_dst):
                self.error("Input file already exists in the archive...")

            if os.path.isdir(self.input_to_add):
                shutil.copytree(self.input_to_add, arc_dst)
            else:
                shutil.copy(self.input_to_add, arc_dst)

            self.input = self.extracted_dir

        def compress_output(self):
            self.compress()

        extract_arc(self)
        navigate_in_extracted(self)
        copy_input_to_extracted(self)
        compress_output(self)


Archives().main()
