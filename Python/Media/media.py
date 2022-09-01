#!/usr/bin/python3
# Media menu, usado para imagens, videos e audios

import os
import subprocess
from Tfuncs import gmenu, inpt, oupt


class Media:
    def __init__(self):
        self.img_exts = 'jpg', 'png'
        self.vid_exts = 'mp4', 'avi', 'm4v', 'mov'
        self.aud_exts = 'mp3', 'm4b', 'opus', 'wav'

    def compress_img(self):
        def compress_img(img_in, quality, special_opts, img_out):
            cmd = f"convert \"{img_in}\" {special_opts} -sampling-factor " \
                  f"4:2:0 -strip -quality {quality} -interlace Plane " \
                  f"\"{img_out}\""
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {img_in}")
            
        img_in = input("Enter the input img or folder: ")
        if os.path.isdir(img_in):
            img_in_dir = img_in
            img_in = [os.path.join(img_in, img) for img in os.listdir(img_in)
                      if img.endswith(self.img_exts)]
        elif os.path.isfile(img_in):
            img_in = inpt.files(question="Enter de img input full path: ",
                                extensions=self.img_exts,
                                file_input=img_in)
            if img_in == 'q':
                print('Aborted...')
                return
        else:
            print('Aborted...')
            return

        if type(img_in) is not list:
            img_out = oupt.files(question="Enter the img output full path, "
                                 "or just the name for same input dir, "
                                 "or leave empty for <input>_output.jpg: ",
                                 extension='jpg', file_input=img_in)
            if img_out == 'q':
                print('Aborted...')
                return

        while True:
            quality = input("Enter the quality of the output image (1-100) "
                            "\n(85-70 recommended, don't go below 50) "
                            "or leave empty for 70: ")
            if quality == 'q':
                print('Aborted...')
                return
            elif quality == '':
                quality = '70'
                break

            try:
                if int(quality) not in range(1, 101):
                    print('Quality must be between 1 and 100...')
                    continue
                break
            except ValueError:
                print('Quality must be a number...')
                continue

        special_opts = ''
        #if input("Want to apply any special option, that might decrease size "
        #         "a bit more, but change the image? (y/N): ") == 'y':

        #    ''' Alterar o número de blur (0.05) altera apenas o blur,
        #    mantendo o tamanho de armazenamento'''
        #    if input("Want to apply a little blur? (y/N): ") == 'y':
        #        special_opts += '-gaussian-blur 0.05'

        #    if input("Want to apply colorspace RGB (img might become darker)? "
        #             "(y/N): ") == 'y':
        #        special_opts += ' -colorspace RGB'

        if type(img_in) is list:
            output_dir = os.path.join(img_in_dir, f'Compressed_{quality}%_quality')
            if os.path.isdir(output_dir):
                print("Output folder already exists\nAborting...")
                return
            os.mkdir(output_dir)
            for img in img_in:
                img_basename = os.path.basename(img)
                img_basename_out = os.path.splitext(img_basename)[0] + '.jpg'
                img_out = os.path.join(output_dir, img_basename_out)
                compress_img(img, quality, special_opts, img_out)
        else:
            compress_img(img_in, quality, special_opts, img_out)

    @staticmethod
    def change_img_format():
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

    def compress_vid(self):
        def compress_vid(vid_in, vid_out):
            # Comprime apenas vid, e mantém o som; qt maior -crf, maior compres
            cmd = f"ffmpeg -i \"{vid_in}\" -vcodec libx265 -crf 28 -acodec " \
                  f"copy \"{vid_out}\""
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {vid_in}")

        vid_in = input("Enter the input video or folder: ")
        if os.path.isdir(vid_in):
            vid_in_dir = vid_in
            vid_in = [os.path.join(vid_in, vid) for vid in os.listdir(vid_in)
                      if vid.endswith(self.vid_exts)]
        elif os.path.isfile(vid_in):
            vid_in = inpt.files(question="Enter de video input full path: ",
                                extensions=self.vid_exts,
                                file_input=vid_in)
            if vid_in == 'q':
                print('Aborted...')
                return
        else:
            print('Aborted...')
            return

        if type(vid_in) is not list:
            vid_out = oupt.files(question="Enter the video output full path, "
                                 "or just the name for same input dir, "
                                 "or leave empty for <input>_output.mp4: ",
                                 extension='mp4', file_input=vid_in)
            if vid_out == 'q':
                print('Aborted...')
                return

            compress_vid(vid_in, vid_out)
        else:
            output_dir = os.path.join(vid_in_dir, 'Compressed')
            if os.path.isdir(output_dir):
                print("Output folder already exists\nAborting...")
                return
            os.mkdir(output_dir)
            for vid in vid_in:
                vid_basename = os.path.basename(vid)
                vid_basename_out = os.path.splitext(vid_basename)[0] + '.mp4'
                vid_out = os.path.join(output_dir, vid_basename_out)
                compress_vid(vid, vid_out)

    def compress_aud(self):
        def compress_aud(aud_in, aud_out, concatenate=False):
            # 32Kb de bitrate não é bom para música
            if concatenate:
                cmd = f"ffmpeg -f concat -safe 0 -i \"{aud_in}\" " \
                      "-c:a libopus -b:a 32k -vbr on -compression_level 10 " \
                      f"-frame_duration 60 -application voip \"{aud_out}\""
            else:
                cmd = f"ffmpeg -i \"{aud_in}\" -c:a libopus -b:a 32k " \
                      "-vbr on -compression_level 10 -frame_duration 60 " \
                      f"-application voip \"{aud_out}\""
            err = subprocess.call(cmd, shell=True)
            if err != 0:
                print(f"Error compressing {aud_in}")

        aud_in = input("Enter the input audio or folder: ")
        if os.path.isdir(aud_in):
            aud_in_dir = aud_in
            aud_in = [os.path.join(aud_in, aud) for aud in os.listdir(aud_in)
                      if aud.endswith(self.aud_exts)]
        elif os.path.isfile(aud_in):
            aud_in = inpt.files(question="Enter de audio input full path: ",
                                extensions=self.aud_exts,
                                file_input=aud_in)
            if aud_in == 'q':
                print('Aborted...')
                return
        else:
            print('Aborted...')
            return

        if type(aud_in) is not list:
            aud_out = oupt.files(question="Enter the audio output full path, "
                                 "or just the name for same input dir, "
                                 "or leave empty for <input>_output.opus: ",
                                 extension='opus', file_input=aud_in)
            if aud_out == 'q':
                print('Aborted...')
                return

            compress_aud(aud_in, aud_out)
        else:
            if input(":: Do you want to concatenate the audio files? [y/N] ") \
                    .lower() == 'y':

                output_dir = os.path.join(aud_in_dir, 'Compressed_and_concat')
                if os.path.isdir(output_dir):
                    print("Output folder already exists\nAborting...")
                    return
                os.mkdir(output_dir)
                aud_out = os.path.join(output_dir, "output.opus")

                aud_in_txt = os.path.join(aud_in_dir, 'input_files.txt')
                aud_in = sorted(aud_in)
                with open(aud_in_txt, 'w') as txt:
                    for aud in aud_in:
                        entry = f"file '{aud}'"
                        print(entry)
                        txt.write(entry + '\n')

                if input(":: Do you want to edit the list of audio files to "
                         "be concatenated? [y/N] ").lower() == 'y':
                    cmd = f"nvim \"{aud_in_txt}\""
                    subprocess.run(cmd, shell=True)

                compress_aud(aud_in_txt, aud_out, concatenate=True)
            else:
                output_dir = os.path.join(aud_in_dir, 'Compressed')
                if os.path.isdir(output_dir):
                    print("Output folder already exists\nAborting...")
                    return
                os.mkdir(output_dir)

                for aud in aud_in:
                    aud_basename = os.path.basename(aud)
                    aud_out = os.path.join(output_dir, aud_basename)
                    compress_aud(aud, aud_out)


med = Media()
title = 'Media-Menu'
keys = {'ic': (med.compress_img, "compress image or folder of images"),
        'if': (med.change_img_format, "convert image format"),
        'ocr': (med.ocr, "read image with an OCR"),
        'vc': (med.compress_vid, "compress video or folder of videos"),
        'ac': (med.compress_aud, "compress audio or folder of audios")}
gmenu(title, keys)
