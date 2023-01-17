import math
from getpass import getpass
from typing import Optional

from utils import Utils, FileType


class Pdf:
    utils = Utils()

    def compress(self) -> None:
        pdf_ins = self.utils.get_input(FileType.PDF, accept_dirs=True)
        if not pdf_ins:
            print("Aborted...")
            return

        pdf_outs = self.utils.get_output(pdf_ins, output_dirname="Compressed")

        compress_options = {
            "1": "printer",
            "2": "ebook",
            "3": "default",
            "4": "screen",
        }
        compress_option = self._get_compression_option(compress_options)
        if compress_option is None:
            return

        for pdf_in, pdf_out in zip(pdf_ins, pdf_outs):
            err = self.utils.compress_pdf(pdf_in, pdf_out, compress_option)
            if err != 0:
                print(f"Error compressing {pdf_in}\nAborted...")
                return
        print("Compression done")

    def _get_compression_option(
        self, compress_options: dict[str, str]
    ) -> Optional[str]:
        prompt = input(
            "From [1] (best quality, recommended) to [4] (worst quality)"
            "\nEnter the level of compression: "
        )
        if prompt == "q":
            print("Aborted...")
            return None
        try:
            return compress_options[prompt]
        except KeyError:
            print("Invalid option")
            return None

    def merge(self) -> None:
        pdf_ins = self.utils.get_input(
            FileType.PDF, allow_multiple_prompts=True
        )
        if not pdf_ins or pdf_ins is str:
            print("Aborted...")
            return

        pdf_out = self.utils.get_output(pdf_ins[0], output_dirname="Merged")

        pdf_in = " ".join(pdf_ins)
        err = self.utils.merge_pdf(pdf_in, pdf_out)
        if err != 0:
            print(f"Error merging {pdf_in}\nAborted...")
            return
        print("Merge complete")

    def split(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return

        pdf_out = self.utils.get_output(pdf_in, output_dirname="Splited")
        pdf_out = pdf_out.split(".pdf")[0]

        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)
        pages = self._get_pages_to_split(total_pages)
        if pages is None:
            return

        print("Wait a moment...")
        for page in pages.split():
            pdf_out = f"{pdf_out}_{page}.pdf"
            err = self.utils.split_pdf(pdf_in, pdf_out, page)
            if err != 0:
                print(f"Error spliting {pdf_in}\nAborted...")
                return
        print("Split complete")

    def _get_pages_to_split(self, total_pages: int) -> Optional[str]:
        # improve func
        while True:
            pages = input(
                "Enter the pages to split (e.g.: 1-5 6-15 16-end);"
                "\nOr enter the <#> to try to split in <#> "
                "similar parts: "
            )
            if pages == "q":
                print("Aborted...")
                return None

            try:
                parts = int(pages)
                if 2 <= parts <= total_pages:
                    increment = math.floor(total_pages / parts)
                    pages = ""
                    pf_last = 0
                    for p in range(parts):
                        pi = pf_last + 1
                        if p == parts - 1:
                            pf = "z"
                        else:
                            pf = pi + increment - 1
                        pf_last = pf
                        part = f"{pi}-{pf} "
                        pages += part
                    return pages
            except ValueError:
                pass

            if "-end" in pages:
                pages_list = pages.split()
                validation = True
                pf_last, pf = 0, 0
                for p in pages_list:
                    pi = p.split("-")[0]
                    self.utils.page_num_within_total(pi, total_pages)
                    if p != pages_list[-1]:
                        pf = p.split("-")[1]
                        self.utils.page_num_within_total(pf, total_pages)
                        if int(pi) >= int(pf):
                            validation = False
                            break
                    if int(pi) != int(pf_last) + 1:
                        validation = False
                        break
                    pf_last = pf
                if validation:
                    pages = pages.replace("end", "z")
                    return pages
            print("Invalid answer")

    def encrypt(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return
        pdf_out = self.utils.get_output(pdf_in, output_dirname="Encrypted")

        while True:
            crypt_pass = getpass(
                prompt="Enter the password to encrypt the PDF: "
            )
            crypt_pass2 = getpass(prompt="Enter again the same password: ")
            if crypt_pass == crypt_pass2:
                break
            print("Passwords are different, try again...")

        err = self.utils.encrypt_pdf(pdf_in, pdf_out, crypt_pass)
        if err != 0:
            print(f"Error encrypting {pdf_in}\nAborted...")
            return

    def decrypt(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return
        pdf_out = self.utils.get_output(pdf_in, output_dirname="Decrypted")

        crypt_pass = getpass(prompt="Enter the crypt password of the PDF: ")

        err = self.utils.decrypt_pdf(pdf_in, pdf_out, crypt_pass)
        if err != 0:
            print(f"Error decrypting {pdf_in}\nAborted...")
            return

    def rotate(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return

        pdf_out = self.utils.get_output(pdf_in, output_dirname="Rotated")

        rotation_options = {"1": "+90", "2": "-90", "3": "+180"}
        rotation = self._get_rotation_angle(rotation_options)
        if not rotation:
            return

        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)
        pages = self._get_pages_to_rotate(total_pages)
        if not pages:
            return

        err = self.utils.rotate_pdf(pdf_in, pdf_out, rotation, pages)
        if err != 0:
            print(f"Error rotating {pdf_in}\nAborted...")
            return

    def _get_rotation_angle(
        self, rotation_options: dict[str, str]
    ) -> Optional[str]:
        prompt = input(
            "[1]: Rotate 90º\n[2]: Rotate -90º\n[3]: Rotate 180º\nChoose: "
        )
        if prompt == "q":
            print("Aborted...")
            return None
        try:
            return rotation_options[prompt]
        except KeyError:
            print("Invalid option")
            return None

    def _get_pages_to_rotate(self, total_pages: int) -> Optional[str]:
        while True:
            pages = input(
                "Enter the pages to rotate (e.g.: 4 or 1+14+5+10 or "
                "7-end);\nOr leave empty for whole PDF: "
            )
            if pages == "q":
                print("Aborted...")
                return None
            elif pages == "":
                return "1-z"
            elif "-end" in pages:
                first_page = pages.split("-")[0]
                if not self.utils.page_num_within_total(
                    int(first_page), total_pages
                ):
                    continue
                return first_page + "-z"
            elif "+" in pages:
                pages_are_all_valid = True
                for page in pages.split("+"):
                    if not self.utils.page_num_within_total(
                        int(page), total_pages
                    ):
                        pages_are_all_valid = False
                if pages_are_all_valid:
                    return pages.replace("+", ",")
            elif len(pages.split("-")) == 2:
                return pages
            print("Invalid answer")

    def ocr(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return

        img_out = self.utils.get_output(
            pdf_in, output_dirname="OCR'ed", output_file_extension=".png"
        )

        self.utils.pdf_to_img(pdf_in, img_out)

        txt_out = img_out[0] + ".txt"
        with open(txt_out, "w") as f:
            for n, img in enumerate(sorted(img_out), 1):
                text = self.utils.get_text_from_img(img)
                f.write("\n" + "-" * 40 + f"[PAGE {n}]" + "-" * 40 + "\n\n")
                f.writelines(text)

        if input(":: Do you want to open the txt? [Y/n] ") in ("", "Y", "y"):
            self.utils.open_in_vim(txt_out)

    def convert_from_img(self) -> None:
        img_ins = self.utils.get_input(
            FileType.IMG, allow_multiple_prompts=True
        )
        if not img_ins:
            print("Aborted...")
            return
        elif img_ins is str:
            img_in = img_ins
        else:
            img_in = img_ins[0]

        pdf_out = self.utils.get_output(
            img_in, output_dirname="Pdf_from_img", output_file_extension=".pdf"
        )

        print("Wait a moment...")
        if img_ins is list and len(img_ins) > 1:
            resolution = self._get_resolution_for_img(img_ins)
        else:
            resolution = self.utils.get_img_resolution(img_in)

        err = self.utils.img_to_pdf(img_ins, pdf_out, resolution)
        if err != 0:
            print(f"Error converting {img_ins}\nAborted...")
            return

    def _get_resolution_for_img(self, img_ins: list[str]) -> tuple[int, int]:
        # change this... incorporate in func above, or in utils func
        img_ins_heights = [
            self.utils.get_img_resolution(img_in, only_height=True)
            for img_in in img_ins
        ]

        smallest_img_index = img_ins_heights.index(min(img_ins_heights))
        smallest_img = img_ins[smallest_img_index]
        return self.utils.get_img_resolution(smallest_img)

    def convert_to_img(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return

        img_out = self.utils.get_output(
            pdf_in, output_dirname="Img_from_pdf", output_file_extension=".png"
        )

        self.utils.pdf_to_img(pdf_in, img_out)

    def change_pdf_title(self) -> None:
        pdf_in = self.utils.get_input(FileType.PDF)
        if not pdf_in:
            print("Aborted...")
            return

        pdf_out = self.utils.get_output(pdf_in, output_dirname="New_title")

        new_title = input("Enter the new title for the pdf: ")
        if new_title == "q":
            print("Aborted...")
            return

        err = self.utils.change_pdf_title(pdf_in, pdf_out, new_title)
        if err != 0:
            print(f"Error changing title")
