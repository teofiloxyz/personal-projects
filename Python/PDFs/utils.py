#!/usr/bin/python3

import os
import subprocess


class Utils:
    @staticmethod
    def get_pdf_input(
        accept_dirs: bool = False, allow_multiple_prompts: bool = False
    ) -> str | list[str]:
        # This function needs rework
        if accept_dirs and allow_multiple_prompts:
            print("Shouldn't have both args True.")
            return "q"

        if accept_dirs:
            question = "Enter the PDF input or dir path: "
        else:
            question = "Enter the PDF input path: "

        if allow_multiple_prompts:
            question += "(Leave empty to proceed) "
            pdfs_in = list()
            prompt = input(question)
            if not prompt.endswith(".pdf"):
                print("Input has to be a pdf file...")
            else:
                pdfs_in.append(prompt)
            while prompt != "":
                prompt = input(question)
                if not prompt.endswith(".pdf"):
                    print("Input has to be a pdf file...")
                    continue
                pdfs_in.append(prompt)
            return pdfs_in

        prompt = input(question)
        if os.path.isdir(prompt):
            return [
                os.path.join(root_dirs_files[0], file)
                for root_dirs_files in os.walk(prompt)
                for file in root_dirs_files[2]
                if file.endswith(".pdf")
            ]
        if not prompt.endswith(".pdf"):
            return prompt
        return "q"

    @staticmethod
    def get_pdf_output(pdf_in: str | list[str]) -> str | list[str]:
        # This function needs rework

        if pdf_in is str:
            pdf_out = pdf_in.strip(".pdf") + "_output.pdf"
            while os.path.isfile(pdf_out):
                pdf_out = "_" + pdf_out
            return pdf_out

        output_dir = os.path.dirname(pdf_in[0]) + "Output"
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return [os.path.join(output_dir, file) for file in pdf_in]

    @staticmethod
    def get_img_input(
        accept_dirs: bool = False, allow_multiple_prompts: bool = False
    ) -> str | list[str]:
        # This function needs rework
        if accept_dirs and allow_multiple_prompts:
            print("Shouldn't have both args True.")
            return "q"

        if accept_dirs:
            question = "Enter the image input or dir path: "
        else:
            question = "Enter the image input path: "

        if allow_multiple_prompts:
            question += "(Leave empty to proceed) "
            pdfs_in = list()
            prompt = input(question)
            if not prompt.endswith((".jpg", ".png")):
                print("Input has to be a jpg or png file...")
            else:
                pdfs_in.append(prompt)
            while prompt != "":
                prompt = input(question)
                if not prompt.endswith((".jpg", ".png")):
                    print("Input has to be a jpg or png file...")
                    continue
                pdfs_in.append(prompt)
            return pdfs_in

        prompt = input(question)
        if os.path.isdir(prompt):
            return [
                os.path.join(root_dirs_files[0], file)
                for root_dirs_files in os.walk(prompt)
                for file in root_dirs_files[2]
                if file.endswith((".jpg", ".png"))
            ]
        if not prompt.endswith((".jpg", ".png")):
            return prompt
        return "q"

    @staticmethod
    def get_img_output(img_in: str | list[str]) -> str | list[str]:
        # This function needs rework

        if img_in is str:
            img_out = img_in.strip(".jpg") + "_output.jpg"
            while os.path.isfile(img_out):
                img_out = "_" + img_out
            return img_out

        output_dir = os.path.dirname(img_in[0]) + "Output"
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return [os.path.join(output_dir, file) for file in img_in]

    @staticmethod
    def get_pdf_num_of_pages(pdf_in: str) -> int:
        return int(
            subprocess.run(
                ["qpdf", "--show-npages", pdf_in], capture_output=True
            ).stdout.decode("utf-8")
        )

    @staticmethod
    def page_num_within_total(page_num: int, pdf_total_pages: int) -> bool:
        if page_num > pdf_total_pages:
            print(f"PDF only has {pdf_total_pages} pages")
            return False
        return True

    def run_cmd(self, cmd: str) -> int:
        print("Wait a moment...")
        return subprocess.call(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def compress_pdf(self, pdf_in: str, pdf_out: str, compress_opt: str) -> int:
        cmd = f"ps2pdf -dPDFSETTINGS=/{compress_opt} {pdf_in} {pdf_out}"
        return self.run_cmd(cmd)

    def merge_pdf(self, pdf_ins: str, pdf_out: str) -> int:
        cmd = f"qpdf --empty --pages {pdf_ins} -- {pdf_out}"
        return self.run_cmd(cmd)

    def split_pdf(self, pdf_in: str, pdf_out: str, page: str) -> int:
        cmd = f"qpdf --empty --pages {pdf_in} {page} -- {pdf_out}"
        return self.run_cmd(cmd)

    def encrypt_pdf(self, pdf_in: str, pdf_out: str, crypt_pass: str) -> int:
        cmd = (
            f"qpdf --encrypt {crypt_pass} {crypt_pass} 256 -- "
            f"{pdf_in} {pdf_out}"
        )
        return self.run_cmd(cmd)

    def decrypt_pdf(self, pdf_in: str, pdf_out: str, crypt_pass: str) -> int:
        cmd = f"qpdf --decrypt --password={crypt_pass} {pdf_in} {pdf_out}"
        return self.run_cmd(cmd)

    def rotate_pdf(
        self, pdf_in: str, pdf_out: str, rotation: str, pages: str
    ) -> int:
        cmd = f"qpdf {pdf_in} {pdf_out} --rotate={rotation}:{pages}"
        return self.run_cmd(cmd)

    def pdf_to_img(self, pdf_in: str, img_out: str) -> int:
        cmd = f"pdftoppm -png {pdf_in} {img_out}"
        return self.run_cmd(cmd)

    def img_to_pdf(self, img_ins: str, pdf_out: str, resolution: str) -> int:
        cmd = f"convert -resize {resolution} -density 300 {img_ins} {pdf_out}"
        return self.run_cmd(cmd)

    def get_img_resolution(self, img_in: str, only_height: bool = False) -> str:
        res_format = "%h" if only_height else "%wx%h"
        return subprocess.run(
            ["identify", "-format", res_format, img_in],
            capture_output=True,
        ).stdout.decode("utf-8")

    def ocr_img(self, img_in: str, txt_out: str) -> int:
        cmd = f"tesseract {img_in} {txt_out}"
        return self.run_cmd(cmd)

    def open_txt(self, txt: str) -> int:
        cmd = f"nvim {txt}"
        return self.run_cmd(cmd)
