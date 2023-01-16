#!/usr/bin/python3
# Menu PDF com diversas funções
# Utils need rework on input output funcs
# Menu also need rework and fixing

from Tfuncs import gmenu

from pdf import Pdf


def main() -> None:
    open_menu()


def open_menu() -> None:
    pdf = Pdf()
    title = "PDF-Menu"
    keys = {
        "c": (pdf.compress_pdf, "compress PDF or folder of PDF's"),
        "m": (pdf.merge_pdf, "merge (concatenate) PDF's"),
        "s": (pdf.split_pdf, "split PDF"),
        "ec": (pdf.encrypt_pdf, "encrypt PDF (AES-256)"),
        "dc": (pdf.decrypt_pdf, "decrypt PDF"),
        "r": (pdf.rotate_pdf, "rotate PDF"),
        "o": (pdf.ocr, "read PDF with OCR"),
        "ip": (pdf.convert_img_to_pdf, "convert images into PDF"),
        "pi": (pdf.convert_pdf_to_img, "convert PDF into images"),
        "t": (pdf.change_pdf_title, "change pdf title (not filename)"),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
