from utils import Utils


class Image:
    utils = Utils()
    image_exts = "jpg", "png"
    output_ext = "jpg"

    def compress(self) -> None:
        images = self.utils.get_input(self.image_exts)
        if len(images) == 0:
            print("Aborted...")
            return

        image_qlt = self._get_compression_qlt()
        if image_qlt == "q":
            print("Aborted...")
            return

        special_opts = self._get_compress_special_opts()
        output_dir = self.utils.create_output_dir(
            images, title=f"Compressed_{image_qlt}%_quality"
        )
        images = self.utils.get_output(images, output_dir, self.output_ext)

        [
            self._compress_image(image, image_qlt, special_opts)
            for image in images
        ]

    def convert(self) -> None:
        images = self.utils.get_input(self.image_exts)
        if len(images) == 0:
            print("Aborted...")
            return

        output_dir = self.utils.create_output_dir(images, title="Converted")
        images = self.utils.get_output_alternate_ext(images, output_dir)
        [self._convert_image(image) for image in images]

    def ocr(self) -> None:
        image = self.utils.get_input(self.image_exts, only_one_file=True)
        if len(image) == 0:
            print("Aborted...")
            return

        output_dir = self.utils.create_output_dir(image, title="OCR")
        image = self.utils.get_output(image, output_dir, ".txt")
        language = self._get_orc_language()
        self._ocr_image(image[0]["input"], image[0]["output"], language)

    def _get_compression_qlt(self) -> str:
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

    def _get_compress_special_opts(self) -> str:
        special_opts = ""
        prompt = input(
            ":: Want to apply any special option, that might decrease size "
            "a bit more, but change the image? [y/N] "
        )
        if prompt.lower() == "y":
            return special_opts

        """Alterar o número de blur (0.05) altera apenas o blur,
        mantendo o tamanho de armazenamento"""
        if input(":: Want to apply a little blur? [y/N] ") == "y":
            special_opts += " -gaussian-blur 0.05"
        prompt = input(
            ":: Want to apply colorspace RGB (img might become darker)? [y/N] "
        )
        if prompt.lower() == "y":
            special_opts += " -colorspace RGB"
        return special_opts

    def _compress_image(
        self, image: dict, image_qlt: str, special_opts: str
    ) -> None:
        cmd = (
            f'convert "{image["input"]}" {special_opts} -sampling-factor '
            f"4:2:0 -strip -quality {image_qlt} -interlace Plane "
            f'"{image["output"]}"'
        )
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error compressing {image['input']}")

    def _convert_image(self, image: dict) -> None:
        cmd = f"convert {image['input']} {image['output']}"
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error converting {image['input']}")

    def _get_orc_language(self) -> str:
        return input(
            "Enter the language of the image (for multiple languages "
            "e.g.: por+eng)\nOr leave empty for auto (not recommended): "
        )

    def _ocr_image(
        self, image_input: str, txt_output: str, language: str
    ) -> None:
        cmd = f"tesseract {image_input} {txt_output}"
        if language != "":
            cmd += f" -l {language}"
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error OCR'ing {image_input}")

        if input(":: Open the txt output? [Y/n] ") in ("", "Y", "y"):
            self.utils.open_on_vim(txt_output)
