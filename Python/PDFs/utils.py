import os
import subprocess
from enum import Enum, auto
from typing import Optional


class FileType(Enum):
    PDF = auto()
    IMG = auto()

    def get_file_ext(self) -> str | tuple[str, str]:
        if self == FileType.PDF:
            return ".pdf"
        elif self == FileType.IMG:
            return ".jpg", ".png"


class Utils:
    def get_input(
        self,
        file_type: FileType,
        accept_dirs: bool = False,
        allow_multiple_prompts: bool = False,
    ) -> Optional[str | list[str]]:
        if accept_dirs:
            return self._get_input_from_dir(file_type.get_file_ext())
        elif allow_multiple_prompts:
            return self._get_multiple_inputs(file_type.get_file_ext())
        else:
            return self._get_single_input(file_type.get_file_ext())

    def get_output(
        self,
        input_path: str | list[str],
        output_dirname: str,
        output_file_extension: str | None = None,
    ) -> str | list[str]:
        output_dir = self._create_output_dir(input_path, output_dirname)
        if input_path is str:
            return self._get_single_output(
                input_path, output_dir, output_file_extension
            )
        else:
            return self._get_multiple_outputs(
                input_path, output_dir, output_file_extension
            )

    @staticmethod
    def _get_input_from_dir(file_extensions: str | tuple) -> Optional[list]:
        """Prompts for a directory path and
        returns all files with the specified extension(s)"""

        prompt = input("Enter the directory path: ")
        if os.path.isdir(prompt):
            return [
                os.path.join(root_dirs_files[0], file)
                for root_dirs_files in os.walk(prompt)
                for file in root_dirs_files[2]
                if file.endswith(file_extensions)
            ]
        elif prompt == "q":
            return None
        else:
            print(f"{prompt} is not a valid directory")
            return None

    @staticmethod
    def _get_multiple_inputs(file_extensions: str | tuple) -> Optional[list]:
        """Prompts for multiple files paths and
        returns all files with the specified extension(s)"""

        prompt = input(
            f"Enter the {file_extensions} input path (Leave empty to proceed): "
        )
        input_files = []
        while prompt != "":
            if prompt == "q":
                return None
            elif not prompt.endswith(file_extensions):
                print(f"Input has to be a {file_extensions} file...")
            else:
                input_files.append(prompt)
            prompt = input(
                f"Enter the {file_extensions} input path (Leave empty to proceed): "
            )
        return input_files

    @staticmethod
    def _get_single_input(file_extensions: str | tuple) -> Optional[str]:
        """Prompts for a single file path and
        returns the path if it has the specified extension(s)"""

        prompt = input(f"Enter the {file_extensions} input path: ")
        if prompt == "q":
            return None
        if not prompt.endswith(file_extensions):
            print(f"Input has to be a {file_extensions} file...")
            return None
        return prompt

    def _get_single_output(
        self,
        input_file: str,
        output_dir: str,
        output_file_extension: str | None = None,
    ) -> str:
        """Creates output path for a single input file"""

        input_file_basename = os.path.basename(input_file)
        input_file_name, input_file_ext = os.path.splitext(input_file_basename)
        if not output_file_extension:
            output_file_extension = input_file_ext
        else:
            if not output_file_extension.startswith("."):
                output_file_extension = "." + output_file_extension
        return os.path.join(output_dir, input_file_name + output_file_extension)

    def _get_multiple_outputs(
        self,
        input_files: list[str],
        output_dir: str,
        output_file_extension: str | None = None,
    ) -> list:
        return [
            self._get_single_output(
                input_file, output_dir, output_file_extension
            )
            for input_file in input_files
        ]

    @staticmethod
    def _create_output_dir(
        input_path: str | list[str], output_dirname: str
    ) -> str:
        if input_path is list:
            input_path = input_path[0]
        input_dir = os.path.dirname(input_path)
        output_dir = os.path.join(input_dir, output_dirname)

        if os.path.exists(output_dir):
            i = 1
            while os.path.exists(f"{output_dir}_{i}"):
                i += 1
            output_dir = f"{output_dir}_{i}"

        os.mkdir(output_dir)
        return output_dir

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

    def compress_pdf(self, pdf_in: str, pdf_out: str, compress_opt: str) -> int:
        cmd = f"ps2pdf -dPDFSETTINGS=/{compress_opt} {pdf_in} {pdf_out}"
        return self._run_cmd(cmd)

    def merge_pdf(self, pdf_ins: str, pdf_out: str) -> int:
        cmd = f"qpdf --empty --pages {pdf_ins} -- {pdf_out}"
        return self._run_cmd(cmd)

    def split_pdf(self, pdf_in: str, pdf_out: str, page: str) -> int:
        cmd = f"qpdf --empty --pages {pdf_in} {page} -- {pdf_out}"
        return self._run_cmd(cmd)

    def encrypt_pdf(self, pdf_in: str, pdf_out: str, crypt_pass: str) -> int:
        cmd = (
            f"qpdf --encrypt {crypt_pass} {crypt_pass} 256 -- "
            f"{pdf_in} {pdf_out}"
        )
        return self._run_cmd(cmd)

    def decrypt_pdf(self, pdf_in: str, pdf_out: str, crypt_pass: str) -> int:
        cmd = f"qpdf --decrypt --password={crypt_pass} {pdf_in} {pdf_out}"
        return self._run_cmd(cmd)

    def rotate_pdf(
        self, pdf_in: str, pdf_out: str, rotation: str, pages: str
    ) -> int:
        cmd = f"qpdf {pdf_in} {pdf_out} --rotate={rotation}:{pages}"
        return self._run_cmd(cmd)

    def pdf_to_img(self, pdf_in: str, img_out: str) -> int:
        cmd = f"pdftoppm -png {pdf_in} {img_out}"
        return self._run_cmd(cmd)

    def img_to_pdf(self, img_ins: str, pdf_out: str, resolution: str) -> int:
        cmd = f"convert -resize {resolution} -density 300 {img_ins} {pdf_out}"
        return self._run_cmd(cmd)

    def get_img_resolution(self, img_in: str, only_height: bool = False) -> str:
        res_format = "%h" if only_height else "%wx%h"
        return subprocess.run(
            ["identify", "-format", res_format, img_in],
            capture_output=True,
        ).stdout.decode("utf-8")

    def ocr_img(self, img_in: str, txt_out: str) -> int:
        cmd = f"tesseract {img_in} {txt_out}"
        return self._run_cmd(cmd)

    def change_pdf_title(
        self, pdf_in: str, pdf_out: str, new_title: str
    ) -> int:
        cmd = f'exiftool -Title="{new_title}" "{pdf_in}" -out "{pdf_out}"'
        return self._run_cmd(cmd)

    def open_txt(self, txt: str) -> int:
        cmd = f"nvim {txt}"
        return self._run_cmd(cmd)

    @staticmethod
    def _run_cmd(cmd: str) -> int:
        print("Wait a moment...")
        return subprocess.call(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
