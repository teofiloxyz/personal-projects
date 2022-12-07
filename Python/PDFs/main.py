#!/usr/bin/python3
# Menu PDF com diversas funções

import os
import shutil
import subprocess
import math
from getpass import getpass
from Tfuncs import gmenu, qst, inpt, oupt


if __name__ == "__main__":
    pdf = PDFs()
    title = "PDF-Menu"
    keys = {
        "c": (pdf.compress_pdf, "compress PDF"),
        "cf": (pdf.compress_folder, "compress all PDF's in a folder"),
        "m": (pdf.merge_pdf, "merge (concatenate) PDFs"),
        "s": (pdf.split_pdf, "split PDF"),
        "ec": (pdf.encrypt_pdf, "encrypt PDF (AES-256)"),
        "dc": (pdf.decrypt_pdf, "decrypt PDF"),
        "r": (pdf.rotate_pdf, "rotate PDF"),
        "o": (pdf.ocr, "read PDF with OCR"),
        "ip": (pdf.convert_img_to_pdf, "convert images into PDF"),
        "pi": (pdf.convert_pdf_to_img, "convert PDF into images"),
    }
    gmenu(title, keys)
