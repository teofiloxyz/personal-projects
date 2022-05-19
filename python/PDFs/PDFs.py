#!/usr/bin/python3
# Menu PDF com diversas funções

import os
import shutil
import subprocess
import math
from getpass import getpass
from Tfuncs import gmenu, qst, inpt, oupt


class PDFs:
    @staticmethod
    def compress_pdf():
        pdf_in = inpt.files(question='Enter the PDF input full path: ',
                            extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_out = oupt.files(question='Enter the PDF output full path, or '
                             ' just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=pdf_in)
        if pdf_out == 'q':
            print('Aborted...')
            return

        compress_opts = {'1': 'printer',
                         '2': 'ebook',
                         '3': 'default',
                         '4': 'screen'}
        compress = qst.opts(question='From [1] (best quality, recommended) '
                            'to [4] (worst quality)\nEnter the level of '
                            'compression: ', opts_dict=compress_opts)
        if compress == 'q':
            print('Aborted...')
            return

        print('Wait a moment...')
        cmd = f'ps2pdf -dPDFSETTINGS=/{compress} {pdf_in} {pdf_out}'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f'Compression done\nOutput at {pdf_out}')

    @staticmethod
    def compress_folder():
        pdfs_dir = inpt.dirs(question='Enter the directory input full path: ')
        if pdfs_dir == 'q':
            print('Aborted...')
            return

        pdf_ins_list = []
        for root_dirs_files in os.walk(str(pdfs_dir)):
            for file in root_dirs_files[2]:
                if file.endswith('.pdf'):
                    pdf_ins_list.append(os.path.join(root_dirs_files[0], file))

        if len(pdf_ins_list) == 0:
            print('No PDF files in given directory, aborted...')
            return

        compress_opts = {'1': 'printer',
                         '2': 'ebook',
                         '3': 'default',
                         '4': 'screen'}
        compress = qst.opts(question='From [1] (best quality, recommended) to '
                            '[4] (worst quality)\nEnter the level of '
                            'compression: ', opts_dict=compress_opts)
        if compress == 'q':
            print('Aborted...')
            return

        print('Wait a moment...')
        compressed_dir = os.path.join(str(pdfs_dir), 'compressed')
        os.mkdir(compressed_dir)

        for pdf_in in pdf_ins_list:
            pdf_in_name = os.path.basename(pdf_in)
            pdf_out = os.path.join(compressed_dir, pdf_in_name)
            cmd = f'ps2pdf -dPDFSETTINGS=/{compress} {pdf_in} {pdf_out}'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        print(f'Compression done\nOutput at {compressed_dir}')

    @staticmethod
    def merge_pdf():
        print('Enter as many PDF inputs as you want to merge, but in order')
        pdf_ins_list = inpt.files(question='Enter the PDF input full path, '
                                  'when done leave empty to proceed: ',
                                  extensions='pdf', multiple=True)
        if pdf_ins_list == 'q':
            print('Aborted...')
            return

        pdf_ins = ' '.join(pdf_ins_list)

        pdf_out = oupt.files(question='Enter the PDF output full path, or '
                             'just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=pdf_ins_list[-1])
        if pdf_out == 'q':
            print('Aborted...')
            return

        print('Wait a moment...')
        cmd = f'qpdf --empty --pages {pdf_ins} -- {pdf_out}'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f'Merge complete\nOutput at {pdf_out}')

    def split_pdf(self):
        pdf_in = inpt.files(question='Enter the PDF input full path: ',
                            extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_in_dir = os.path.dirname(str(pdf_in))
        pdf_in_name = os.path.basename(str(pdf_in))
        total_pages = self.get_pdf_pgnum(pdf_in)

        while True:
            pages = input('Enter the pages to split (e.g.: 1-5 6-15 16-end);'
                          '\nOr enter the <#> to try to split in <#> '
                          'similar parts: ')
            if pages == 'q':
                print('Aborted...')
                return

            try:
                if 2 <= int(pages) <= int(total_pages):
                    parts = int(pages)
                    increment = math.floor(int(total_pages) / parts)
                    pages = ''
                    pf_last = 0
                    for p in range(parts):
                        pi = int(pf_last) + 1
                        if p == parts - 1:
                            pf = 'z'
                        else:
                            pf = pi + increment - 1
                        pf_last = pf
                        part = str(pi) + '-' + str(pf) + ' '
                        pages += part
                    break
            except ValueError:
                pass

            if '-end' in pages:
                pages_list = pages.split()
                validation = True
                pf_last, pf = 0, 0
                for p in pages_list:
                    pi = p.split('-')[0]
                    self.validate_page_num(pi, total_pages)
                    if p != pages_list[-1]:
                        pf = p.split('-')[1]
                        self.validate_page_num(pf, total_pages)
                        if int(pi) >= int(pf):
                            validation = False
                            break
                    if int(pi) != int(pf_last) + 1:
                        validation = False
                        break
                    pf_last = pf
                if validation is False:
                    print('Invalid answer')
                    continue
                pages = pages.replace('end', 'z')
                break
            print('Invalid answer')

        print('Wait a moment...')
        for p in pages.split():
            pdf_out = pdf_in_dir + pdf_in_name + '_' + p + '.pdf'
            cmd = f'qpdf --empty --pages {pdf_in} {p} -- {pdf_out}'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        print('Split complete')

    @staticmethod
    def encrypt_pdf():
        print("Why don't you use GPG or SSL to encrypt the file?")
        pdf_in = inpt.files(question='Enter the PDF to encrypt full path: ',
                            extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_out = oupt.files(question='Enter the PDF output full path, '
                             'or just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=pdf_in)
        if pdf_out == 'q':
            print('Aborted...')
            return

        while True:
            crypt_pass = getpass(prompt='Enter the password to '
                                 'encrypt the PDF: ')
            crypt_pass2 = getpass(prompt='Enter again the same password: ')
            if crypt_pass == crypt_pass2:
                break
            print('Passwords are different, try again...')

        cmd = f'qpdf --encrypt {crypt_pass} {crypt_pass} 256 -- ' \
              f'{pdf_in} {pdf_out}'
        subprocess.run(cmd, shell=True)
        print(f'Encryption done\nOutput at {pdf_out}')

    @staticmethod
    def decrypt_pdf():
        pdf_in = inpt.files(question='Enter the PDF to decrypt full path: ',
                            extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_out = oupt.files(question='Enter the PDF output full path, or '
                             'just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=pdf_in)
        if pdf_out == 'q':
            print('Aborted...')
            return

        crypt_pass = getpass(prompt='Enter the crypt password of the PDF: ')
        cmd = f'qpdf --decrypt --password={crypt_pass} {pdf_in} {pdf_out}'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f'Decryption done\nOutput at {pdf_out}')

    def rotate_pdf(self):
        pdf_in = inpt.files(question='Enter the PDF to decrypt full path: ',
                            extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_out = oupt.files(question='Enter the PDF output full path, or '
                             'just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=pdf_in)
        if pdf_out == 'q':
            print('Aborted...')
            return

        rotation_opts = {'1': '+90',
                         '2': '-90',
                         '3': '+180'}
        rotation = qst.opts(question='[1]: Rotate 90º\n[2]: Rotate -90º\n[3]: '
                            'Rotate 180º\nChoose: ', opts_dict=rotation_opts)
        if rotation == 'q':
            print('Aborted...')
            return

        total_pages = self.get_pdf_pgnum(pdf_in)

        while True:
            pages = input('Enter the pages to rotate (e.g.: 4 or 1+14+5+10 or '
                          '7-end);\nOr leave empty for whole PDF: ')
            if pages == 'q':
                print('Aborted...')
                return
            elif pages == '':
                pages = '1-z'
                break
            elif '-end' in pages:
                if self.validate_page_num(pages.split('-')[0],
                                          total_pages) is False:
                    continue
                pages = str(pages.split('-')[0]) + '-z'
                break
            elif '+' in pages:
                pages = pages.replace('+', ',')
                validation = None
                for p in pages.split(','):
                    if self.validate_page_num(p, total_pages) is False:
                        validation = False
                if validation is not False:
                    break
            print('Invalid answer')

        cmd = f'qpdf {pdf_in} {pdf_out} --rotate={rotation}:{pages}'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f'Rotation done\nOutput at {pdf_out}')

    @staticmethod
    def ocr():
        pdf_in = inpt.files(question='Enter the PDF to read '
                            'full path: ', extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        lang = input('Enter the language of the pdf (for multiple languages '
                     'e.g.: por+eng)\nor leave empty for auto '
                     '(not recomended): ')

        img_dir = '/tmp/pdf_menu_ocr/'
        if not os.path.isdir(img_dir):
            os.mkdir(img_dir)

        print('Wait a moment...')
        cmd = f'pdftoppm -png {pdf_in} {img_dir}'
        subprocess.run(cmd, shell=True)

        txt_final = str(pdf_in) + '_ocr.txt'
        if os.path.isfile(txt_final):
            os.remove(txt_final)

        for n, img in enumerate(sorted(os.listdir(img_dir)), 1):
            img = os.path.join(img_dir, img)
            cmd = f'tesseract {img} {img}'
            txt = img + '.txt'
            if lang != '':
                cmd = cmd + f' -l {lang}'
            subprocess.run(cmd, shell=True)
            with open(txt, 'r') as tx:
                page = tx.readlines()
            with open(txt_final, 'a') as tx:
                tx.write('\n' + '-' * 40 + f'[PAGE {n}]' + '-' * 40 + '\n\n')
                tx.writelines(page)

        shutil.rmtree(img_dir, ignore_errors=True)
        print(f'Done!\nTxt file at {txt_final}')

        if input(':: Do you want to open the txt? [Y/n] ') in ('', 'Y', 'y'):
            cmd = f'nvim {txt_final}'
            subprocess.run(cmd, shell=True)

    @staticmethod
    def convert_img_to_pdf():
        print('Enter as many image files as you want to merge in one PDF, but '
              'in order')
        img_ins_list = inpt.files(question='Enter the image input full path, '
                                  'when done leave empty to proceed: ',
                                  extensions=('png', 'jpg'), multiple=True)
        if img_ins_list == 'q':
            print('Aborted...')
            return

        img_ins = ' '.join(img_ins_list)

        pdf_out = oupt.files(question='Enter the PDF output full path, or '
                             'just the name for same input dir, or leave '
                             'empty for <input>_output.pdf: ',
                             extension='pdf', file_input=img_ins_list[-1])
        if pdf_out == 'q':
            print('Aborted...')
            return

        print('Wait a moment...')
        if len(img_ins_list) > 1:
            img_res_height_list = \
                [subprocess.run(['identify', '-format', '"%h"', img],
                                capture_output=True).stdout.decode('utf-8')
                 for img in img_ins_list]

            smallest_img_index = img_res_height_list \
                .index(min(img_res_height_list))
            smallest_img = img_ins_list[smallest_img_index]
            resolution = \
                subprocess.run(['identify', '-format',
                                '"%wx%h"', smallest_img],
                               capture_output=True) \
                .stdout.decode('utf-8')

            cmd = f'convert -resize {resolution} -density 300 ' \
                  f'{img_ins} {pdf_out}'

        else:
            cmd = f'convert -density 300 {img_ins} {pdf_out}'

        subprocess.run(cmd, shell=True)
        print(f'Conversion complete\nOutput at {pdf_out}')

    @staticmethod
    def convert_pdf_to_img():
        pdf_in = inpt.files(question='Enter the PDF to convert to images '
                            'full path: ', extensions='pdf')
        if pdf_in == 'q':
            print('Aborted...')
            return

        pdf_name = os.path.splitext(os.path.basename(str(pdf_in)))[0]
        pdf_dir = os.path.dirname(str(pdf_in))

        out_dir = os.path.join(pdf_dir, 'Output_' + pdf_name)
        while os.path.isdir(out_dir):
            out_dir_name = os.path.basename(out_dir)
            n = out_dir_name.split('Output_')[0]
            if n == '':
                out_dir = os.path.join(pdf_dir, '2Output_' + pdf_name)
            else:
                out_dir = os.path.join(pdf_dir, str(int(n) + 1)
                                       + 'Output_' + pdf_name)
        os.mkdir(out_dir)

        print('Wait a moment...')
        cmd = f'pdftoppm -png {pdf_in} {out_dir}/{pdf_name}'
        subprocess.run(cmd, shell=True)
        print(f'Done!\nOutput at {out_dir}')

    @staticmethod
    def validate_page_num(page_num, total_pages):
        try:
            page_num = int(page_num)
        except ValueError:
            print('Write digits, not letters')
            return False

        if page_num > total_pages:
            print(f'PDF input only has {total_pages} pages')
            return False

    @staticmethod
    def get_pdf_pgnum(pdf_in):
        page_num = subprocess.run(['qpdf', '--show-npages', pdf_in],
                                  capture_output=True) \
            .stdout.decode('utf-8')
        return int(page_num)


if __name__ == "__main__":
    pdf = PDFs()
    title = 'PDF-Menu'
    keys = {'c': (pdf.compress_pdf, "compress PDF"),
            'cf': (pdf.compress_folder, "compress all PDF's in a folder"),
            'm': (pdf.merge_pdf, "merge (concatenate) PDFs"),
            's': (pdf.split_pdf, "split PDF"),
            'ec': (pdf.encrypt_pdf, "encrypt PDF (AES-256)"),
            'dc': (pdf.decrypt_pdf, "decrypt PDF"),
            'r': (pdf.rotate_pdf, "rotate PDF"),
            'o': (pdf.ocr, "read PDF with OCR"),
            'ip': (pdf.convert_img_to_pdf, "convert images into PDF"),
            'pi': (pdf.convert_pdf_to_img, "convert PDF into images")}
    gmenu(title, keys)
