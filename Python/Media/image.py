#!/usr/bin/python3

import os
import subprocess


class Image:
    def __init__(self) -> None:
        self.img_exts = "jpg", "png"

    def compress(self) -> None:
        img_in = self.get_input()
        if len(img_in) == 0:
            print("Aborted...")
            return

        img_qlt = self.get_compression_qlt()
        if img_qlt == "q":
            print("Aborted...")
            return

        special_opts = (
            ""
            if (
                input(
                    ":: Want to apply any special option, that might decrease size "
                    "a bit more, but change the image? [y/N] "
                )
                == "y"
            )
            else self.get_compress_special_opts()
        )

        output_dir = self.create_output_dir(img_in, img_qlt)
        img_in_out = self.get_input_output(img_in, output_dir)

        [
            self.compress_img(img_in, img_out, img_qlt, special_opts)
            for img_in, img_out in img_in_out.items()
        ]

    def convert(self) -> None:
        # Melhorar input
        img_in = self.get_input()
        if len(img_in) == 0:
            print("Aborted...")
            return

        # Melhorar para mais formatos no futuro
        img_path, in_ext = os.path.splitext(img_in[0])
        out_ext = ".png" if in_ext == ".jpg" else ".jpg"
        img_out = img_path + out_ext

        self.convert_img(img_in[0], img_out)

    def ocr(self) -> None:
        # Melhorar input
        img_in = self.get_input()
        if len(img_in) == 0:
            print("Aborted...")
            return

        output = os.path.splitext(img_in[0])[0]

        self.ocr_img(img_in[0], output)

    def get_input(self) -> list[str]:
        prompt = input("Enter the path of image or folder with images: ")
        if os.path.isdir(prompt):
            return [
                os.path.join(prompt, image)
                for image in os.listdir(prompt)
                if image.endswith(self.img_exts)
            ]
        elif os.path.isfile(prompt):
            if prompt.endswith(self.img_exts):
                return [prompt]
            else:
                print(f"Accepted formats are: {'; '.join(self.img_exts)}")
        return []

    def create_output_dir(self, img_in: list[str], img_quality: str) -> str:
        img_in_dir = os.path.dirname(img_in[0])
        output_dir = os.path.join(
            img_in_dir, f"Compressed_{img_quality}%_quality"
        )
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return output_dir

    def get_input_output(
        self, img_in: list[str], output_dir: str
    ) -> dict[str, str]:
        img_in_out = dict()
        for img in img_in:
            img_in_basename = os.path.basename(img)
            img_in_bn_no_ext = os.path.splitext(img_in_basename)[0]
            img_out_basename = img_in_bn_no_ext + ".jpg"
            img_out = os.path.join(output_dir, img_out_basename)
            img_in_out[img] = img_out
        return img_in_out

    def get_compression_qlt(self) -> str:
        while True:
            quality = input(
                "Enter the quality of the output image (1-100) "
                "\n(85-70 recommended, don't go below 50) "
                "or leave empty for 70: "
            )
            if quality == "q":
                return quality
            elif quality == "":
                quality = "70"
                return quality

            try:
                if int(quality) not in range(1, 101):
                    print("Quality must be between 1 and 100...")
                    continue
                return quality
            except ValueError:
                print("Quality must be a number...")
                continue

    def get_compress_special_opts(self) -> str:
        special_opts = ""

        """Alterar o número de blur (0.05) altera apenas o blur,
        mantendo o tamanho de armazenamento"""
        if input(":: Want to apply a little blur? [y/N] ") == "y":
            special_opts += "-gaussian-blur 0.05"

        if (
            input(
                ":: Want to apply colorspace RGB (img might become darker)? "
                "[y/N] "
            )
            == "y"
        ):
            special_opts += " -colorspace RGB"
        return special_opts

    def compress_img(
        self, img_in: str, img_out: str, quality: str, special_opts: str
    ) -> None:
        cmd = (
            f'convert "{img_in}" {special_opts} -sampling-factor '
            f"4:2:0 -strip -quality {quality} -interlace Plane "
            f'"{img_out}"'
        )
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print(f"Error compressing {img_in}")

    def convert_img(self, img_in: str, img_out: str) -> None:
        cmd = f"convert {img_in} {img_out}"
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print(f"Error converting {img_in}")

    def ocr_img(self, img_in: str, txt_out: str) -> None:
        # refactor!
        lang = input(
            "Enter the language of the image (for multiple languages "
            "e.g.: por+eng)\nOr leave empty for auto (not recommended): "
        )

        cmd = f"tesseract {img_in} {txt_out}"
        if lang != "":
            cmd += f" -l {lang}"
        err = subprocess.call(cmd, shell=True)
        if err != 0:
            print(f"Error OCR'ing {img_in}")

        if input(":: Open the txt output? [Y/n] ") in ("", "Y", "y"):
            cmd = f"nvim {txt_out}.txt"
            subprocess.run(cmd, shell=True)
