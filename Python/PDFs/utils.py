#!/usr/bin/python3


class Utils:
    def validate_page_num(page_num, total_pages):
        try:
            page_num = int(page_num)
        except ValueError:
            print("Write digits, not letters")
            return False

        if page_num > total_pages:
            print(f"PDF input only has {total_pages} pages")
            return False

    def get_pdf_pgnum(pdf_in):
        page_num = subprocess.run(
            ["qpdf", "--show-npages", pdf_in], capture_output=True
        ).stdout.decode("utf-8")
        return int(page_num)
