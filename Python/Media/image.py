#!/usr/bin/python3


class Image:
    # self.img_exts = "jpg", "png"
    def compress_img(self):
        def compress_img(img_in, quality, special_opts, img_out):
            cmd = (
                f'convert "{img_in}" {special_opts} -sampling-factor '
                f"4:2:0 -strip -quality {quality} -interlace Plane "
                f'"{img_out}"'
            )
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {img_in}")

        img_in = input("Enter the input img or folder: ")
        if os.path.isdir(img_in):
            img_in_dir = img_in
            img_in = [
                os.path.join(img_in, img)
                for img in os.listdir(img_in)
                if img.endswith(self.img_exts)
            ]
        elif os.path.isfile(img_in):
            img_in = inpt.files(
                question="Enter de img input full path: ",
                extensions=self.img_exts,
                file_input=img_in,
            )
            if img_in == "q":
                print("Aborted...")
                return
        else:
            print("Aborted...")
            return

        if type(img_in) is not list:
            img_out = oupt.files(
                question="Enter the img output full path, "
                "or just the name for same input dir, "
                "or leave empty for <input>_output.jpg: ",
                extension="jpg",
                file_input=img_in,
            )
            if img_out == "q":
                print("Aborted...")
                return

        while True:
            quality = input(
                "Enter the quality of the output image (1-100) "
                "\n(85-70 recommended, don't go below 50) "
                "or leave empty for 70: "
            )
            if quality == "q":
                print("Aborted...")
                return
            elif quality == "":
                quality = "70"
                break

            try:
                if int(quality) not in range(1, 101):
                    print("Quality must be between 1 and 100...")
                    continue
                break
            except ValueError:
                print("Quality must be a number...")
                continue

        special_opts = ""
        # if input("Want to apply any special option, that might decrease size "
        #         "a bit more, but change the image? (y/N): ") == 'y':

        #    ''' Alterar o número de blur (0.05) altera apenas o blur,
        #    mantendo o tamanho de armazenamento'''
        #    if input("Want to apply a little blur? (y/N): ") == 'y':
        #        special_opts += '-gaussian-blur 0.05'

        #    if input("Want to apply colorspace RGB (img might become darker)? "
        #             "(y/N): ") == 'y':
        #        special_opts += ' -colorspace RGB'

        if type(img_in) is list:
            output_dir = os.path.join(
                img_in_dir, f"Compressed_{quality}%_quality"
            )
            if os.path.isdir(output_dir):
                print("Output folder already exists\nAborting...")
                return
            os.mkdir(output_dir)
            for img in img_in:
                img_basename = os.path.basename(img)
                img_basename_out = os.path.splitext(img_basename)[0] + ".jpg"
                img_out = os.path.join(output_dir, img_basename_out)
                compress_img(img, quality, special_opts, img_out)
        else:
            compress_img(img_in, quality, special_opts, img_out)

    @staticmethod
    def change_img_format():
        img_in = inpt.files(
            question="Enter de img input full path: ", extensions=("jpg", "png")
        )
        if img_in == "q":
            print("Aborted...")
            return

        # Melhorar para mais formatos no futuro
        in_ext = os.path.splitext(str(img_in))[-1]
        out_ext = "png" if in_ext == ".jpg" else "jpg"

        img_out = oupt.files(
            question="Enter the img output full path, "
            "or just the name for same input dir, or "
            f"leave empty for <input>_output.{out_ext}: ",
            extension=out_ext,
            file_input=img_in,
        )
        if img_out == "q":
            print("Aborted...")
            return

        subprocess.run(["convert", img_in, img_out])

    @staticmethod
    def ocr():
        img_in = inpt.files(
            question="Enter the img input full path: ",
            extensions=("jpg", "png"),
        )

        txt_out = oupt.files(
            question="Enter the txt output full path, "
            "or just the name for same input dir, "
            "or leave empty for <input>.txt: ",
            extension=None,
            file_input=img_in,
        )

        lang = input(
            "Enter the language of the image (for multiple languages "
            "e.g.: por+eng)\nor leave empty for auto "
            "(not recommended): "
        )

        cmd = f"tesseract {img_in} {txt_out}"
        if lang != "":
            cmd = cmd + f" -l {lang}"
        subprocess.run(cmd, shell=True)

        open_output = input(":: Do you want to open the output? [Y/n] ")
        if open_output in ("", "Y", "y"):
            cmd = f"nvim {txt_out}.txt"
            subprocess.run(cmd, shell=True)
