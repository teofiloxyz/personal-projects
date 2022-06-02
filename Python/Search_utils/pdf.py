#!/usr/bin/python3

import os
import sys
import subprocess
import fitz  # need PyMuPDF module installed
from Tfuncs import inpt, rofi


class Pdf:
    def main(self, entry):
        self.entry = entry.split()
        if self.get_files_list():
            self.get_number_of_pages()
            if self.search_entry():
                self.rofi_dmenu()
                if self.choice != "":
                    self.open_choice()

    def get_files_list(self):
        '''Eu sei que com "shell=True" é possível fazer uma "shell injection"
        através do prompt. No entanto, isso não é possível visto que a função
        "inpt.dirs" só aceita dirs válidos...'''
        question = 'Enter the directory to search'
        self.dir_path = inpt.dirs(question, use_rofi=True)
        # $fd é apenas pela piada, pois podia usar os.walk()
        cmd = 'fd --hidden --absolute-path --type file --extension pdf ' \
              f'--base-directory {self.dir_path}'
        self.files_list = subprocess.run(cmd, shell=True, capture_output=True)\
            .stdout.decode('utf-8').split('\n')[:-1]

        self.number_of_pdfs = len(self.files_list)
        if self.number_of_pdfs == 0:
            rofi.message("Didn't found any pdf file in the provided directory")
            return False
        return True

    def get_number_of_pages(self):
        message = f'Found {self.number_of_pdfs} pdf files in the provided ' \
                  'directory.\n'

        total_pages = 0
        for file in self.files_list:
            cmd = f'qpdf --show-npages {file}'
            page_num = subprocess.run(cmd, shell=True, capture_output=True) \
                .stdout.decode('utf-8')
            if page_num == '':
                message += f'Cannot access {file} is it encrypted?\n'
                self.files_list.remove(file)
                continue
            total_pages += int(page_num)

        message += f'Total number of pages is {total_pages}\n'
        if 100 >= total_pages > 25:
            message += 'Search might take a while.'
        elif total_pages > 100:
            message += 'Search might take a long time.'
        else:
            message += 'Search should be quick.'

        rofi.message(message)

    def search_entry(self):
        self.results = {}
        output_dir = '/tmp/search_util_PDF/'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        result_num = 1
        for file in self.files_list:
            pdf = fitz.open(file)
            for n, page in enumerate(pdf, 1):
                text = page.get_text()
                if text == '':
                    cmd = f'pdftoppm -f {n} -l {n} -png {file} {output_dir}'
                    subprocess.run(cmd, shell=True)
                    output = f'{output_dir}/-{n}.png'
                    cmd = f'tesseract {output} {output} -l por'
                    subprocess.run(cmd, shell=True)
                    ocr = f'{output}.txt'
                    with open(ocr, 'r') as tx:
                        text = tx.read()

                for entry in self.entry:
                    if entry.lower() in text.lower():
                        self.results[str(result_num)] = file, n
                        result_num += 1

        if len(self.results) == 0:
            if type(self.entry) is list:
                self.entry = "' or '".join(self.entry)
            rofi.message(f"Didn't find any pdf file with '{self.entry}'")
            return False
        return True

    def rofi_dmenu(self):
        prompt = 'Choose which one to open'
        dmenu = [f"Page {result[1]} in "
                 f"...{os.path.dirname(result[0]).split('/')[-1]}/"
                 f"{os.path.basename(result[0])}"
                 for result in self.results.values()]
        self.choice = rofi.custom_dmenu(prompt, dmenu)

    def open_choice(self):
        page, file = self.choice.split(" in ...")
        page = page.split("Page ")[-1]
        for result in self.results.values():
            if result[0].endswith(file) and str(result[1]) == page:
                file = result[0]
                break

        cmd = f'mupdf {file} {page}'
        subprocess.Popen(cmd, shell=True, start_new_session=True)


if len(sys.argv) > 1:
    entry = ' '.join(sys.argv[1:])
    Pdf().main(entry)
else:
    print('Argument needed...')
