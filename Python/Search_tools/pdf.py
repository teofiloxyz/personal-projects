from Tfuncs import rofi

import os
import subprocess

# import fitz  # needs PyMuPDF module installed


class Pdf:
    def main(self, entry: str) -> None:
        search_dir = self.get_search_dir()
        if search_dir == "q":
            rofi.message("Aborted...")
            return

        files = self.get_files(search_dir)
        if len(files) == 0:
            rofi.message("Didn't found any pdf file in the provided directory")
            return

        number_of_pages = self.get_number_of_pages(files)
        self.get_message_of_search(files, number_of_pages)

        output_dir = self.create_output_dir()
        results = dict()
        for file in files:
            file_results = self.search_entry_in_file(file, entry, output_dir)
            if len(file_results) == 0:
                continue
            results[file] = file_results
        if len(results) == 0:
            rofi.message(f"Didn't find any pdf file with '{entry}'")
            return

        dmenu_list = self.create_dmenu_list(results)
        choice = self.choose_with_rofi_dmenu(dmenu_list)
        if choice == "":
            return
        file, page = self.process_choice(choice, results)
        self.open_choice(file, page)

    def get_search_dir(self) -> str:
        prompt = rofi.simple_prompt("Enter the directory to search")
        if not os.path.isdir(prompt):
            return "q"
        return prompt

    def get_files(self, search_dir: str) -> list[str]:
        cmd = (
            "fd --hidden --absolute-path --type file --extension pdf "
            f"--base-directory {search_dir}"
        )
        return (
            subprocess.run(cmd, shell=True, capture_output=True)
            .stdout.decode("utf-8")
            .split("\n")[:-1]
        )

    def get_number_of_pages(self, files: list[str]) -> int:
        total_pages = 0
        for file in files:
            cmd = f"qpdf --show-npages {file}"
            page_num = subprocess.run(
                cmd, shell=True, capture_output=True
            ).stdout.decode("utf-8")
            if page_num == "":
                rofi.message(f"Cannot access {file} is it encrypted?")
                files.remove(file)
                continue
            total_pages += int(page_num)
        return total_pages

    def get_message_of_search(
        self, files: list[str], number_of_pages: int
    ) -> None:
        message = (
            f"Found {len(files)} pdf files in the provided " "directory.\n"
        )
        message += f"Total number of pages is {number_of_pages}\n"
        if 100 >= number_of_pages > 25:
            message += "Search might take a while."
        elif number_of_pages > 100:
            message += "Search might take a long time."
        else:
            message += "Search should be quick."
        rofi.message(message)

    def create_output_dir(self) -> str:
        output_dir = "/tmp/search_util_PDF/"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        return output_dir

    def search_entry_in_file(
        self, file: str, entry: str, output_dir: str
    ) -> list[tuple]:
        results = list()
        pdf = fitz.open(file)
        for page_num, page in enumerate(pdf, 1):
            lines = page.get_text()
            if lines == "":
                img = self.get_img_from_page(file, output_dir, str(page_num))
                txt = self.get_txt_from_img(img)
                lines = self.get_file_lines(txt)
            for line in lines:
                if entry.lower() in line.lower():
                    line = " ".join(line.split())  # bc of indentation
                    results.append((page_num, line))
        return results

    def get_img_from_page(
        self, file: str, output_dir: str, page_num: str
    ) -> str:
        cmd = f"pdftoppm -f {page_num} -l {page_num} -png {file} {output_dir}"
        subprocess.run(cmd, shell=True)
        return f"{output_dir}/-{page_num}.png"

    def get_txt_from_img(self, img_file: str, language: str = "por") -> str:
        cmd = f"tesseract {img_file} {img_file} -l {language}"
        subprocess.run(cmd, shell=True)
        return f"{img_file}.txt"

    def get_file_lines(self, file: str) -> list[str]:
        with open(file, "r") as f:
            return f.readlines()

    def create_dmenu_list(self, results: dict) -> list[str]:
        return [
            f"Page {result[1]} in "
            f"...{os.path.dirname(result[0]).split('/')[-1]}/"
            f"{os.path.basename(result[0])}"
            for result in results.values()
        ]

    def choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open"
        return rofi.custom_dmenu(prompt, dmenu)

    def process_choice(self, choice: str, results: dict) -> tuple[str, str]:
        page, file = choice.split(" in ...")
        page = page.split("Page ")[-1]
        for result in results.values():
            if result[0].endswith(file) and str(result[1]) == page:
                file = result[0]
                break
        return file, page

    def open_choice(self, file: str, page: str) -> None:
        cmd = f"mupdf {file} {page}"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
