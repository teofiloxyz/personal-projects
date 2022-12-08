#!/usr/bin/python3
# Menu PDF com diversas funções
# Utils need rework on input output funcs

from Tfuncs import gmenu

from menu import Menu


def main() -> None:
    open_menu()


def open_menu() -> None:
    menu = Menu()
    title = "PDF-Menu"
    keys = {
        "c": (menu.compress_pdf, "compress PDF or folder of PDF's"),
        "m": (menu.merge_pdf, "merge (concatenate) PDF's"),
        "s": (menu.split_pdf, "split PDF"),
        "ec": (menu.encrypt_pdf, "encrypt PDF (AES-256)"),
        "dc": (menu.decrypt_pdf, "decrypt PDF"),
        "r": (menu.rotate_pdf, "rotate PDF"),
        "o": (menu.ocr, "read PDF with OCR"),
        "ip": (menu.convert_img_to_pdf, "convert images into PDF"),
        "pi": (menu.convert_pdf_to_img, "convert PDF into images"),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
