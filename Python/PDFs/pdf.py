import os
import math
from getpass import getpass

from utils import Utils


class Pdf:
    def __init__(self) -> None:
        self.utils = Utils()

    def compress_pdf(self) -> None:
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
        prompt = input(
            "From [1] (best quality, recommended) to [4] (worst quality)"
            "\nEnter the level of compression: "
        )
        if prompt == "q":
            print("Aborted...")
            return
        try:
            compress_opt = compress_options[prompt]
        except KeyError:
            print("Aborted...")
            return

        for pdf_in, pdf_out in pdfs_in, pdfs_out:
            err = self.utils.compress_pdf(pdf_in, pdf_out, compress_opt)
            if err != 0:
                print("Error compressing PDF")
                return
        print("Compression done")

    def merge_pdf(self) -> None:
        pdfs_in = self.utils.get_pdf_input(allow_multiple_prompts=True)
        if pdfs_in == "q":
            print("Aborted...")
            return

        pdf_out = pdfs_in[0].strip(".pdf") + "_merged.pdf"
        pdf_in = " ".join(pdfs_in)

        self.utils.merge_pdf(pdf_in, pdf_out)
        print("Merge complete")

    def split_pdf(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_in_dir = os.path.dirname(str(pdf_in))
        pdf_in_name = os.path.basename(str(pdf_in))
        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)

        while True:
            pages = input(
                "Enter the pages to split (e.g.: 1-5 6-15 16-end);"
                "\nOr enter the <#> to try to split in <#> "
                "similar parts: "
            )
            if pages == "q":
                print("Aborted...")
                return

            try:
                if 2 <= int(pages) <= int(total_pages):
                    parts = int(pages)
                    increment = math.floor(int(total_pages) / parts)
                    pages = ""
                    pf_last = 0
                    for p in range(parts):
                        pi = int(pf_last) + 1
                        if p == parts - 1:
                            pf = "z"
                        else:
                            pf = pi + increment - 1
                        pf_last = pf
                        part = str(pi) + "-" + str(pf) + " "
                        pages += part
                    break
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
                if validation is False:
                    print("Invalid answer")
                    continue
                pages = pages.replace("end", "z")
                break
            print("Invalid answer")

        print("Wait a moment...")
        for p in pages.split():
            pdf_out = pdf_in_dir + pdf_in_name + "_" + p + ".pdf"
            self.utils.split_pdf(pdf_in, pdf_out, p)
        print("Split complete")

    def encrypt_pdf(self) -> None:
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

        self.utils.encrypt_pdf(pdf_in, pdf_out, crypt_pass)

    def decrypt_pdf(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        crypt_pass = getpass(prompt="Enter the crypt password of the PDF: ")

        self.utils.decrypt_pdf(pdf_in, pdf_out, crypt_pass)

    def rotate_pdf(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        rotation_opts = {"1": "+90", "2": "-90", "3": "+180"}
        prompt = input(
            "[1]: Rotate 90º\n[2]: Rotate -90º\n[3]: Rotate 180º\nChoose: "
        )
        if prompt == "q":
            print("Aborted...")
            return
        try:
            rotation = rotation_opts[prompt]
        except KeyError:
            print("Aborted...")
            return

        total_pages = self.utils.get_pdf_num_of_pages(pdf_in)

        while True:
            pages = input(
                "Enter the pages to rotate (e.g.: 4 or 1+14+5+10 or "
                "7-end);\nOr leave empty for whole PDF: "
            )
            if pages == "q":
                print("Aborted...")
                return
            elif pages == "":
                pages = "1-z"
                break
            elif "-end" in pages:
                if (
                    self.utils.page_num_within_total(
                        pages.split("-")[0], total_pages
                    )
                    is False
                ):
                    continue
                pages = str(pages.split("-")[0]) + "-z"
                break
            elif "+" in pages:
                pages = pages.replace("+", ",")
                validation = None
                for p in pages.split(","):
                    if (
                        self.utils.page_num_within_total(p, total_pages)
                        is False
                    ):
                        validation = False
                if validation is not False:
                    break
            print("Invalid answer")

        self.utils.rotate_pdf(pdf_in, pdf_out, rotation, pages)

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

        txt_final = str(pdf_in) + "_ocr.txt"
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

    def convert_img_to_pdf(self) -> None:
        img_ins = self.utils.get_img_input(allow_multiple_prompts=True)

        img_in = " ".join(img_ins)

        # needs rework
        pdf_out = self.utils.get_pdf_output(img_ins)
        if pdf_out == "q":
            print("Aborted...")
            return

        print("Wait a moment...")
        if len(img_ins) > 1:
            img_res_height_list = [
                self.utils.get_img_resolution(img_in, only_height=True)
                for img_in in img_ins
            ]

            smallest_img_index = img_res_height_list.index(
                min(img_res_height_list)
            )
            smallest_img = img_ins[smallest_img_index]
            resolution = self.utils.get_img_resolution(smallest_img)

            self.utils.img_to_pdf(img_ins, pdf_out, resolution)
        else:
            # fix func "resolution"
            self.utils.img_to_pdf(img_ins, pdf_out)

    def convert_pdf_to_img(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_name = os.path.splitext(os.path.basename(str(pdf_in)))[0]
        pdf_dir = os.path.dirname(str(pdf_in))

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
        cmd = f'exiftool -Title="{new_title}" "{pdf_in}" -out "{pdf_out}"'
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Error changing title")
