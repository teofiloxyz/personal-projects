import fitz  # PyMuPDF module
import pytesseract
from PIL import Image
from Tfuncs import Rofi

import tempfile
from typing import Optional

from utils import Utils


class Pdfs:
    rofi = Rofi()
    utils = Utils()

    def main(self, query: str) -> None:
        search_dir = self._get_search_dir()
        if not search_dir:
            self.rofi.message_box("Aborted...")
            return

        files = self._get_files(search_dir)
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

        output_dir = self._create_output_dir()
        results = {
            file: file_results
            for file, file_results in [
                (file, self._search_entry_in_file(file, query, output_dir))
                for file in files
            ]
            if len(file_results) > 0
        }

        if len(results) == 0:
            self.rofi.message_box(f"Didn't find any pdf file with '{query}'")
            return

        dmenu = self._create_dmenu_from_results(results)
        choice = self._choose_with_rofi_dmenu(dmenu)
        if choice == "":
            return
        file, page = self._process_choice(choice, results)
        self._open_choice(file, page)

    def _get_search_dir(self) -> Optional[str]:
        prompt = self.rofi.simple_prompt("Enter the directory to search")
        if not self.utils.check_if_is_dir(prompt):
            return None
        return prompt

    def _get_files(self, search_dir: str) -> list[str]:
        cmd = f'find {search_dir} -iname "*.pdf" -print'
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

    def _create_output_dir(self) -> str:
        return tempfile.gettempdir()

    def _search_entry_in_file(
        self, file: str, query: str, output_dir: str
    ) -> list[tuple]:
        results = list()
        pdf = fitz.open(file)
        for page_num, page in enumerate(pdf, 1):
            lines = page.get_text()
            if lines == "":
                img = self._get_img_from_page(file, output_dir, str(page_num))
                lines = self._get_text_from_img(img)
            for line in lines:
                if query.lower() in line.lower():
                    line = " ".join(line.split())  # bc of indentation
                    results.append((page_num, line))
        return results

    def _get_img_from_page(
        self, file: str, output_dir: str, page_num: str
    ) -> str:
        cmd = f"pdftoppm -f {page_num} -l {page_num} -png {file} {output_dir}"
        self.utils.run_cmd(cmd)
        return f"{output_dir}/-{page_num}.png"

    def _get_text_from_img(self, img_path: str, language: str = "por") -> list:
        """Get img in grayscale, then get its text"""

        img = Image.open(img_path).convert("L")
        return pytesseract.image_to_string(img, lang=language)

    def _create_dmenu_from_results(self, results: dict) -> list[str]:
        return [
            f"Page {result[1]} in "
            f"...{self.utils.get_dirname(result[0]).split('/')[-1]}/"
            f"{self.utils.get_basename(result[0])}"
            for result in results.values()
        ]

    def _choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open"
        return self.rofi.custom_dmenu(prompt, dmenu)

    def _process_choice(self, choice: str, results: dict) -> tuple[str, str]:
        page, file = choice.split(" in ...")
        page = page.split("Page ")[-1]
        for result in results.values():
            if result[0].endswith(file) and str(result[1]) == page:
                file = result[0]
                break
        return file, page

    def _open_choice(self, file: str, page: str) -> None:
        cmd = f"mupdf {file} {page}"
        self.utils.run_cmd_on_new_shell(cmd)
