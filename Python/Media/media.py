#!/usr/bin/python3
# Media menu, usado para imagens, videos e audios

import os
import subprocess
from Tfuncs import gmenu, inpt, oupt


class Media:
    @staticmethod
    def compress():
        img_in = inpt.files(question="Enter de img input full path: ",
                            extensions=('jpg', 'png'))
        if img_in == 'q':
            print('Aborted...')
            return

        img_out = oupt.files(question="Enter the img output full path, "
                             "or just the name for same input dir, "
                             "or leave empty for <input>_output.jpg: ",
                             extension='jpg', file_input=img_in)
        if img_out == 'q':
            print('Aborted...')
            return

        while True:
            quality = input("Enter the quality of the output image (1-100): ")
            if quality == 'q':
                print('Aborted...')
                return

            try:
                if int(quality) not in range(1, 101):
                    print('Quality must be between 1 and 100...')
                    continue
                break
            except ValueError:
                print('Quality must be a number...')
                continue

        special_opts = ''
        if input("Want to apply any special option, that might decrease size "
                 "a bit more? (y/N): ") == 'y':

            ''' Alterar o número de blur (0.05) altera apenas o blur,
            mantendo o tamanho de armazenamento'''
            if input("Want to apply a little blur? (y/N): ") == 'y':
                special_opts += '-gaussian-blur 0.05'
            else:
                special_opts = ' '

            if input("Want to apply colorspace RGB (img might become darker)? "
                     "(y/N): ") == 'y':
                special_opts += ' -colorspace RGB'
            else:
                special_opts = ''

        cmd = f"convert {img_in} {special_opts} -sampling-factor 4:2:0 " \
              f"-strip -quality {quality} -interlace Plane {img_out}"
        subprocess.run(cmd, shell=True)

    @staticmethod
    def change_format():
        img_in = inpt.files(question="Enter de img input full path: ",
                            extensions=('jpg', 'png'))
        if img_in == 'q':
            print('Aborted...')
            return

        # Melhorar para mais formatos no futuro
        in_ext = os.path.splitext(str(img_in))[-1]
        out_ext = 'png' if in_ext == '.jpg' else 'jpg'

        img_out = oupt.files(question="Enter the img output full path, "
                             "or just the name for same input dir, or "
                             f"leave empty for <input>_output.{out_ext}: ",
                             extension=out_ext, file_input=img_in)
        if img_out == 'q':
            print('Aborted...')
            return

        subprocess.run(["convert", img_in, img_out])

    @staticmethod
    def ocr():
        img_in = inpt.files(question="Enter the img input full path: ",
                            extensions=('jpg', 'png'))

        txt_out = oupt.files(question="Enter the txt output full path, "
                             "or just the name for same input dir, "
                             "or leave empty for <input>.txt: ",
                             extension=None, file_input=img_in)

        lang = input('Enter the language of the image (for multiple languages '
                     'e.g.: por+eng)\nor leave empty for auto '
                     '(not recomended): ')

        cmd = f'tesseract {img_in} {txt_out}'
        if lang != '':
            cmd = cmd + f' -l {lang}'
        subprocess.run(cmd, shell=True)

        open_output = input(':: Do you want to open the output? [Y/n] ')
        if open_output in ('', 'Y', 'y'):
            cmd = f'nvim {txt_out}.txt'
            subprocess.run(cmd, shell=True)


med = Media()
title = 'Media-Menu'
keys = {'c': (med.compress, "compress image"),
        'f': (med.change_format, "convert image format"),
        'o': (med.ocr, "read image with an OCR")}
gmenu(title, keys)
