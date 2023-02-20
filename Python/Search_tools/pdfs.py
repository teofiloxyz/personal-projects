import fitz  # PyMuPDF module
import pytesseract
from PIL import Image
from Tfuncs import Rofi

import tempfile
from dataclasses import dataclass

from utils import Utils


@dataclass
class Result:
    path: str
    rofi_line: str
    page_num: int


class Pdfs:
    ROFI_MAX_LINE_SPACE = 93

    def __init__(self, search_dir: str) -> None:
        self.utils = Utils()
        self.rofi = Rofi()
        self.search_dir = search_dir

    def search(self, query: str) -> None:
        files = self._get_pdf_files()
        if len(files) == 0:
            self.rofi.message_box(
                "Didn't found any pdf file in the provided directory"
            )
            return

        total_number_of_pages = sum(
            [self._get_number_of_pages(file) for file in files]
        )
        message = self._get_message_of_search(files, total_number_of_pages)
        self.rofi.message_box(message)

        results = []
        for file in files:
            with fitz.open(file) as pdf:
                for page_num, page in enumerate(pdf, 1):
                    lines = page.get_text()
                    if lines == "":
                        img = self._get_img_from_page(file, page_num)
                        lines = self._get_text_from_img(img)
                    if query.lower() in lines.lower():
                        results.append(self._create_result(file, page_num))
                        break

        if len(results) == 0:
            self.rofi.message_box(f"Didn't find any pdf file with '{query}'")
            return
        elif len(results) == 1:
            choice = results[0]
        else:
            dmenu = [result.rofi_line for result in results]
            dmenu_choice = self._choose_with_rofi_dmenu(dmenu)
            if dmenu_choice == "":
                return
            choice = results[dmenu.index(dmenu_choice)]
        self._open_choice_with_mupdf(choice)

    def _get_pdf_files(self) -> list[str]:
        cmd = f'find {self.search_dir} -type f -iname "*.pdf"'
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def _get_number_of_pages(self, file_path: str) -> int:
        cmd = f"qpdf --show-npages {file_path}"
        page_num = self.utils.run_cmd_and_get_output(cmd)
        if page_num == "":
            self.rofi.message_box(f"Cannot access {file_path} is it encrypted?")
            return 0
        return int(page_num)

    def _get_message_of_search(
        self, files: list[str], number_of_pages: int
    ) -> str:
        message = f"Found {len(files)} pdf files in the provided directory.\n"
        message += f"Total number of pages is {number_of_pages}\n"
        if 100 >= number_of_pages > 25:
            message += "Search might take a while."
        elif number_of_pages > 100:
            message += "Search might take a long time."
        else:
            message += "Search should be quick."
        return message

    def _get_img_from_page(self, file: str, page_num: int) -> str:
        tmp_file = tempfile.NamedTemporaryFile(delete=True).name
        cmd = f"pdftoppm -f {page_num} -l {page_num} -png {file} {tmp_file}"
        self.utils.run_cmd(cmd)
        tmp_img = f"{tmp_file}-{page_num}.png"
        return tmp_img

    def _get_text_from_img(self, img_path: str, language: str = "por") -> str:
        """Get img in grayscale, then get its text"""

        img = Image.open(img_path).convert("L")
        return pytesseract.image_to_string(img, lang=language)

    def _create_result(self, path: str, page_num: int) -> Result:
        split_path = path.split("/")
        name = split_path[-1]
        last_two_dirs = "/".join(split_path[-3:-1])
        caracters_space = len(name + str(page_num)) + 5 + len(last_two_dirs)
        remaining_space = self.ROFI_MAX_LINE_SPACE - caracters_space
        whitespace = " " * remaining_space
        rofi_line = f"{name}:{page_num}{whitespace}.../{last_two_dirs}"

        return Result(path, rofi_line, page_num)

    def _choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open with mupdf: "
        return self.rofi.custom_dmenu(prompt, dmenu)

    def _open_choice_with_mupdf(self, choice: Result) -> None:
        cmd = f'mupdf "{choice.path}" {choice.page_num}'
        self.utils.run_cmd_on_new_shell(cmd)
