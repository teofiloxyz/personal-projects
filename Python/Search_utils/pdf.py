#!/usr/bin/python3

import os
import sys
import subprocess
import fitz  # need PyMuPDF module also installed
import time
from Tfuncs import qst, ffmt, fcol, inpt


class Pdf:
    def main(self, entry):
        self.entry = entry.split()
        if self.get_files_list() is False:
            exit()
        self.get_number_of_pages()
        if self.search_entry() is False:
            exit()
        if self.open_file() is False:
            exit()

    def get_files_list(self):
        '''Eu sei que com "shell=True" é possível fazer uma "shell injection"
        através do prompt. No entanto, isso não é possível visto que a função 
        "inpt.dirs" só aceita dirs válidos...'''
        self.dir_path = inpt.dirs(question='Enter the directory to search: ')
        cmd = 'fd --hidden --absolute-path --type file --extension pdf ' \
              f'--base-directory {self.dir_path}'
        self.files_list = subprocess.run(cmd, shell=True, capture_output=True)\
            .stdout.decode('utf-8').split('\n')[:-1]

        self.number_of_pdfs = len(self.files_list)
        if self.number_of_pdfs == 0:
            print("Didn't found any pdf file in the provided directory...")
            time.sleep(2)
            return False
        print(f'Found {self.number_of_pdfs} pdf files in the provided '
              'directory.\n')

    def get_number_of_pages(self):
        total_pages = 0
        for file in self.files_list:
            cmd = f'qpdf --show-npages {file}'
            page_num = subprocess.run(cmd, shell=True, capture_output=True) \
            .stdout.decode('utf-8')
            if page_num == '':
                print(f'Cannot access {file} is it encrypted?')
                self.files_list.remove(file)
                continue
            total_pages += int(page_num)

        print(f'Total number of pages is {total_pages}')
        if 100 >= total_pages > 25:
            print('Search might take a while.')
        elif total_pages > 100:
            print('Search might take a long time.')
        print()

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
            print(f"Didn't find any pdf file with '{self.entry}'")
            time.sleep(2)
            return False

        [print(f'[{n}] Page {result[1]} in {ffmt.bold}{fcol.green}'
               f'...{os.path.dirname(result[0]).split("/")[-1]}/'
               f'{os.path.basename(result[0])}{ffmt.reset}')
         for n, result in self.results.items()]

    def open_file(self):
        choice = qst.opts('\nPick the file to open: ', self.results)
        if choice == 'q':
            return False

        file, page = choice
        cmd = f'mupdf {file} {page}'
        subprocess.Popen(cmd, shell=True, start_new_session=True)


if len(sys.argv) > 1:
    entry = ' '.join(sys.argv[1:])
    Pdf().main(entry)
else:
    print('Argument needed...')
