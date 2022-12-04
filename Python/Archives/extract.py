#!/usr/bin/python3


class Extract:
    def __init__(self):
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

            cmd = f"alacritty -e ranger {self.extracted_dir}"
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
