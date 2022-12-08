#!/usr/bin/python3

import os
import subprocess

from utils import Utils


class Menu:
    def __init__(self) -> None:
        self.utils = Utils()

    def compress_pdf(self) -> None:  # falta compress folder
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
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

        print("Wait a moment...")
        cmd = f"ps2pdf -dPDFSETTINGS=/{compress_opt} {pdf_in} {pdf_out}"
        err = subprocess.call(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if err != 0:
            print("Error compressing PDF")
            return
        print(f"Compression done\nOutput at {pdf_out}")

    def merge_pdf(self) -> None:
        print("Enter as many PDF inputs as you want to merge, but in order")
        pdf_in = self.utils.get_pdf_input(multiple=True)
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_ins = " ".join(pdf_ins_list)

        print("Wait a moment...")
        cmd = f"qpdf --empty --pages {pdf_ins} -- {pdf_out}"
        subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Merge complete\nOutput at {pdf_out}")

    def split_pdf(self):
        pdf_in = inpt.files(
            question="Enter the PDF input full path: ", extensions="pdf"
        )
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_in_dir = os.path.dirname(str(pdf_in))
        pdf_in_name = os.path.basename(str(pdf_in))
        total_pages = self.get_pdf_pgnum(pdf_in)

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
                    self.validate_page_num(pi, total_pages)
                    if p != pages_list[-1]:
                        pf = p.split("-")[1]
                        self.validate_page_num(pf, total_pages)
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
            cmd = f"qpdf --empty --pages {pdf_in} {p} -- {pdf_out}"
            subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
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

        cmd = (
            f"qpdf --encrypt {crypt_pass} {crypt_pass} 256 -- "
            f"{pdf_in} {pdf_out}"
        )
        subprocess.run(cmd, shell=True)
        print(f"Encryption done\nOutput at {pdf_out}")

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
        cmd = f"qpdf --decrypt --password={crypt_pass} {pdf_in} {pdf_out}"
        subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Decryption done\nOutput at {pdf_out}")

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
        rotation = qst.opts(
            question="[1]: Rotate 90º\n[2]: Rotate -90º\n[3]: "
            "Rotate 180º\nChoose: ",
            opts_dict=rotation_opts,
        )
        if rotation == "q":
            print("Aborted...")
            return

        total_pages = self.utils.get_pdf_pgnum(pdf_in)

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
                    self.utils.validate_page_num(
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
                    if self.utils.validate_page_num(p, total_pages) is False:
                        validation = False
                if validation is not False:
                    break
            print("Invalid answer")

        cmd = f"qpdf {pdf_in} {pdf_out} --rotate={rotation}:{pages}"
        subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Rotation done\nOutput at {pdf_out}")

    def ocr(self) -> None:
        pdf_in = self.utils.get_pdf_input()
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_out = self.utils.get_pdf_output(pdf_in)
        if pdf_in == "q":
            print("Aborted...")
            return

        lang = input(
            "Enter the language of the pdf (for multiple languages "
            "e.g.: por+eng)\nor leave empty for auto "
            "(not recomended): "
        )

        img_dir = "/tmp/pdf_menu_ocr/"
        if not os.path.isdir(img_dir):
            os.mkdir(img_dir)

        print("Wait a moment...")
        cmd = f"pdftoppm -png {pdf_in} {img_dir}"
        subprocess.run(cmd, shell=True)

        txt_final = str(pdf_in) + "_ocr.txt"
        if os.path.isfile(txt_final):
            os.remove(txt_final)

        for n, img in enumerate(sorted(os.listdir(img_dir)), 1):
            img = os.path.join(img_dir, img)
            cmd = f"tesseract {img} {img}"
            txt = img + ".txt"
            if lang != "":
                cmd = cmd + f" -l {lang}"
            subprocess.run(cmd, shell=True)
            with open(txt, "r") as tx:
                page = tx.readlines()
            with open(txt_final, "a") as tx:
                tx.write("\n" + "-" * 40 + f"[PAGE {n}]" + "-" * 40 + "\n\n")
                tx.writelines(page)

        shutil.rmtree(img_dir, ignore_errors=True)
        print(f"Done!\nTxt file at {txt_final}")

        if input(":: Do you want to open the txt? [Y/n] ") in ("", "Y", "y"):
            cmd = f"nvim {txt_final}"
            subprocess.run(cmd, shell=True)

    def convert_img_to_pdf(self) -> None:
        print(
            "Enter as many image files as you want to merge in one PDF, but "
            "in order"
        )
        img_ins_list = inpt.files(
            question="Enter the image input full path, "
            "when done leave empty to proceed: ",
            extensions=("png", "jpg"),
            multiple=True,
        )
        if img_ins_list == "q":
            print("Aborted...")
            return

        img_ins = " ".join(img_ins_list)

        pdf_out = oupt.files(
            question="Enter the PDF output full path, or "
            "just the name for same input dir, or leave "
            "empty for <input>_output.pdf: ",
            extension="pdf",
            file_input=img_ins_list[-1],
        )
        if pdf_out == "q":
            print("Aborted...")
            return

        print("Wait a moment...")
        if len(img_ins_list) > 1:
            img_res_height_list = [
                subprocess.run(
                    ["identify", "-format", '"%h"', img], capture_output=True
                ).stdout.decode("utf-8")
                for img in img_ins_list
            ]

            smallest_img_index = img_res_height_list.index(
                min(img_res_height_list)
            )
            smallest_img = img_ins_list[smallest_img_index]
            resolution = subprocess.run(
                ["identify", "-format", '"%wx%h"', smallest_img],
                capture_output=True,
            ).stdout.decode("utf-8")

            cmd = (
                f"convert -resize {resolution} -density 300 "
                f"{img_ins} {pdf_out}"
            )

        else:
            cmd = f"convert -density 300 {img_ins} {pdf_out}"

        subprocess.run(cmd, shell=True)
        print(f"Conversion complete\nOutput at {pdf_out}")

    def convert_pdf_to_img(self) -> None:
        pdf_in = inpt.files(
            question="Enter the PDF to convert to images " "full path: ",
            extensions="pdf",
        )
        if pdf_in == "q":
            print("Aborted...")
            return

        pdf_name = os.path.splitext(os.path.basename(str(pdf_in)))[0]
        pdf_dir = os.path.dirname(str(pdf_in))

        out_dir = os.path.join(pdf_dir, "Output_" + pdf_name)
        while os.path.isdir(out_dir):
            out_dir_name = os.path.basename(out_dir)
            n = out_dir_name.split("Output_")[0]
            if n == "":
                out_dir = os.path.join(pdf_dir, "2Output_" + pdf_name)
            else:
                out_dir = os.path.join(
                    pdf_dir, str(int(n) + 1) + "Output_" + pdf_name
                )
        os.mkdir(out_dir)

        print("Wait a moment...")
        cmd = f"pdftoppm -png {pdf_in} {out_dir}/{pdf_name}"
        subprocess.run(cmd, shell=True)
        print(f"Done!\nOutput at {out_dir}")
