#!/usr/bin/python3


class AddToArchive:
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
