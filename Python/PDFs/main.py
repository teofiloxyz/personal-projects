#!/usr/bin/python3
# Menu PDF com diversas funções

from Tfuncs import gmenu

from pdf import Pdf


def main() -> None:
    open_menu()


def open_menu() -> None:
    pdf = Pdf()
    title = "PDF-Menu"
    keys = {
        "c": (pdf.compress, "compress PDF or folder of PDF's"),
        "m": (pdf.merge, "merge (concatenate) PDF's"),
        "s": (pdf.split, "split PDF"),
        "ec": (pdf.encrypt, "encrypt PDF (AES-256)"),
        "dc": (pdf.decrypt, "decrypt PDF"),
        "r": (pdf.rotate, "rotate PDF"),
        "o": (pdf.ocr, "read PDF with OCR"),
        "ip": (pdf.convert_from_img, "convert images into PDF"),
        "pi": (pdf.convert_to_img, "convert PDF into images"),
        "t": (pdf.change_pdf_title, "change pdf title (not the filename)"),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
