#!/usr/bin/python3

import os
import shutil
import subprocess
from datetime import datetime
from configparser import ConfigParser


class OCRSelection:
    def __init__(self):
        self.now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        self.tmp_dir = '/tmp/OCR_script'
        self.img = f'{self.tmp_dir}/img.png'

        self.config = ConfigParser()
        self.config.read('config.ini')
        self.lang = self.config['GENERAL']['language']
        self.terminal = self.config['GENERAL']['terminal']
        self.txt_path = self.config['GENERAL']['txt_path']
        self.txt = os.path.join(self.txt_path, f'/OCR_{self.now}')

    def main(self):
        self.mk_tmp_dir()
        self.screenshot()
        self.ocr_img()
        self.rm_tmp_dir()
        self.open_txt()

    def mk_tmp_dir(self):
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def screenshot(self):
        cmd = f'maim -s {self.img}'
        subprocess.run(cmd, shell=True)

    def ocr_img(self):
        cmd = f'tesseract {self.img} {self.txt}'
        if self.lang is not None:
            cmd = cmd + f' -l {self.lang}'
        subprocess.run(cmd, shell=True)

    def rm_tmp_dir(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def open_txt(self):
        cmd = f"notify-send --urgency=low 'Txt at {self.txt}.txt'"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        cmd = f'{self.terminal} -e nvim {self.txt}.txt'
        subprocess.run(cmd, shell=True)


OCRSelection().main()
