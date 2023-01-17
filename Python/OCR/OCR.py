#!/usr/bin/python3
# Select region to screenshot and read it with OCR

import time
import subprocess
import pytesseract
from PIL import Image


NOW = time.strftime("%Y-%m-%d_%H:%M:%S")
IMG_PATH = f"/tmp/python_OCR_{NOW}.png"
TXT_PATH = f"/tmp/python_OCR_{NOW}"
LANGUAGE = "eng"  # "por"/"eng"/...


def take_screenshot() -> None:
    subprocess.run(["maim", "--select", IMG_PATH])


def read_img_with_ocr() -> None:
    img = Image.open(IMG_PATH).convert("L")
    text = pytesseract.image_to_string(img, lang=LANGUAGE)
    with open(f"{TXT_PATH}.txt", "w") as f:
        f.write(text)


def open_txt_output() -> None:
    subprocess.run(["alacritty", "-e", "nvim", f"{TXT_PATH}.txt"])


def main() -> None:
    take_screenshot()
    read_img_with_ocr()
    open_txt_output()


if __name__ == "__main__":
    main()
