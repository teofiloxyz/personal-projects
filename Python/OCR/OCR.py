#!/usr/bin/python3
# Select region to screenshot and read it with OCR

import time
import subprocess


NOW = time.strftime("%Y-%m-%d_%H:%M:%S")
IMG_PATH = f"/tmp/python_OCR_{NOW}.png"
TXT_PATH = f"/tmp/python_OCR_{NOW}"
LANGUAGE = None  # "por"/"eng"/... default -> eng


def main() -> None:
    take_screenshot()
    read_img_with_ocr()
    open_txt_output()


def take_screenshot() -> None:
    subprocess.run(["maim", "--select", IMG_PATH])


def read_img_with_ocr() -> None:
    cmd = f"tesseract {IMG_PATH} {TXT_PATH}"
    if LANGUAGE is not None:
        cmd += f" -l {LANGUAGE}"
    subprocess.run(cmd, shell=True)


def open_txt_output() -> None:
    subprocess.run(["alacritty", "-e", "nvim", f"{TXT_PATH}.txt"])


if __name__ == "__main__":
    main()
