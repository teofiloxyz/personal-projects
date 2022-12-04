#!/usr/bin/python3


class Compress:
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
                        "zip",
                        "zip",
                        f"zip --junk-paths {self.output}.zip {self.input}",
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
                    "3": ("zip", "zip", f"zip {self.output}.zip {self.input}"),
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
