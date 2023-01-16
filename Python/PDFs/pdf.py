import os
import math
from getpass import getpass
from typing import Optional

from utils import Utils


class Pdf:
    utils = Utils()

    def compress(self) -> None:
        pdfs_in = self.utils.get_pdf_input(accept_dirs=True)
        if pdfs_in == "q":
            print("Aborted...")
            return

        pdfs_out = self.utils.get_pdf_output(pdfs_in)
        if pdfs_out == "q":
            print("Aborted...")
            return

        compress_options = {
            "1": "printer",
            "2": "ebook",
            "3": "default",
            "4": "screen",
        }
        compress_option = self.get_compression_option(compress_options)
        if compress_option is None:
            return

        for pdf_in, pdf_out in zip(pdfs_in, pdfs_out):
            err = self.utils.compress_pdf(pdf_in, pdf_out, compress_option)
            if err != 0:
                print(f"Error compressing {pdf_in}\nAborted...")
                return
        print("Compression done")

    def get_compression_option(
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
        pdf_ins = self.utils.get_pdf_input(allow_multiple_prompts=True)
        if pdf_ins == "q":
            print("Aborted...")
            return

        pdf_out = pdf_ins[0].strip(".pdf") + "_merged.pdf"
        pdf_in = " ".join(pdf_ins)

        err = self.utils.merge_pdf(pdf_in, pdf_out)
        if err != 0:
            print(f"Error merging {pdf_in}\nAborted...")
            return
        print("Merge complete")

    def split(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_in_dir = os.path.dirname(str(pdf_in))
        pdf_in_name = os.path.basename(str(pdf_in))
        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)
        pages = self.get_pages_to_split(total_pages)
        if pages is None:
            return

        print("Wait a moment...")
        for page in pages.split():
            pdf_out = f"{pdf_in_dir}/{pdf_in_name}_{page}.pdf"
            err = self.utils.split_pdf(pdf_in, pdf_out, page)
            if err != 0:
                print(f"Error spliting {pdf_in}\nAborted...")
                return
        print("Split complete")

    def get_pages_to_split(self, total_pages: int) -> Optional[str]:
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
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

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
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        crypt_pass = getpass(prompt="Enter the crypt password of the PDF: ")

        err = self.utils.decrypt_pdf(pdf_in, pdf_out, crypt_pass)
        if err != 0:
            print(f"Error decrypting {pdf_in}\nAborted...")
            return

    def rotate(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_out == "q":
            print("Aborted...")
            return

        rotation_options = {"1": "+90", "2": "-90", "3": "+180"}
        rotation = self.get_rotation_angle(rotation_options)
        if rotation is None:
            return

        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)
        pages = self.get_pages_to_rotate(total_pages)
        if pages is None:
            return

        err = self.utils.rotate_pdf(pdf_in, pdf_out, rotation, pages)
        if err != 0:
            print(f"Error rotating {pdf_in}\nAborted...")
            return

    def get_rotation_angle(
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

    def get_pages_to_rotate(self, total_pages: int) -> Optional[str]:
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
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        img_out = self.utils.get_img_output(pdf_in)
        if img_out == "q":
            print("Aborted...")
            return

        img_dir = "/tmp/pdf_menu_ocr/"
        if not os.path.isdir(img_dir):
            os.mkdir(img_dir)

        self.utils.pdf_to_img(pdf_in, img_out)

        txt_final = pdf_in + "_ocr.txt"
        if os.path.isfile(txt_final):
            os.remove(txt_final)

        for n, img in enumerate(sorted(os.listdir(img_dir)), 1):
            img = os.path.join(img_dir, img)
            self.utils.ocr_img(img, img)
            txt = img + ".txt"
            with open(txt, "r") as tx:
                page = tx.readlines()
            with open(txt_final, "a") as tx:
                tx.write("\n" + "-" * 40 + f"[PAGE {n}]" + "-" * 40 + "\n\n")
                tx.writelines(page)

        if input(":: Do you want to open the txt? [Y/n] ") in ("", "Y", "y"):
            self.utils.open_txt(txt_final)

    def convert_from_img(self) -> None:
        img_ins = self.utils.get_img_input(allow_multiple_prompts=True)
        if not img_ins:
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(img_ins[0])
        if pdf_out == "q":
            print("Aborted...")
            return

        print("Wait a moment...")
        if len(img_ins) > 1:
            resolution = self.get_resolution_for_img(img_ins)
        else:
            resolution = self.utils.get_img_resolution(img_ins[0])

        err = self.utils.img_to_pdf(img_ins, pdf_out, resolution)
        if err != 0:
            print(f"Error converting {img_ins}\nAborted...")
            return

    def get_resolution_for_img(self, img_ins: list[str]) -> tuple[int, int]:
        # change this... incorporate in func above, or in utils func
        img_ins_heights = [
            self.utils.get_img_resolution(img_in, only_height=True)
            for img_in in img_ins
        ]

        smallest_img_index = img_ins_heights.index(min(img_ins_heights))
        smallest_img = img_ins[smallest_img_index]
        return self.utils.get_img_resolution(smallest_img)

    def convert_to_img(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_name = os.path.splitext(os.path.basename(str(pdf_in)))[0]
        pdf_dir = os.path.dirname(str(pdf_in))

        # create output dir in utils
        out_dir = os.path.join(pdf_dir, "Output_" + pdf_name)
        while os.path.isdir(out_dir):
            out_dir += "_"
        os.mkdir(out_dir)

        img_out = f"{out_dir}/{pdf_name}"
        self.utils.pdf_to_img(pdf_in, img_out)

    def change_pdf_title(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        new_title = input("Enter the new title for the pdf: ")

        # func in utils
        cmd = f'exiftool -Title="{new_title}" "{pdf_in}" -out "{pdf_out}"'
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error changing title")
