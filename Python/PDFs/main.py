#!/usr/bin/python3
# Menu PDF com diversas funções

from Tfuncs import Menu

from pdf import Pdf


def main() -> None:
    pdf = Pdf()
    menu = Menu(title="PDF-Menu")

    menu.add_option(
        key="c", func=pdf.compress, help="compress PDF or folder of PDF's"
    )
    menu.add_option(key="m", func=pdf.merge, help="merge (concatenate) PDF's")
    menu.add_option(key="s", func=pdf.split, help="split PDF")
    menu.add_option(key="ec", func=pdf.encrypt, help="encrypt PDF (AES-256)")
    menu.add_option(key="dc", func=pdf.decrypt, help="decrypt PDF")
    menu.add_option(key="r", func=pdf.rotate, help="rotate PDF")
    menu.add_option(key="o", func=pdf.ocr, help="read PDF with OCR")
    menu.add_option(
        key="ip", func=pdf.convert_from_img, help="convert images into PDF"
    )
    menu.add_option(
        key="pi", func=pdf.convert_to_img, help="convert PDF into images"
    )
    menu.add_option(
        key="t",
        func=pdf.change_pdf_title,
        help="change pdf title (not the filename)",
    )

    menu.start()


if __name__ == "__main__":
    main()
