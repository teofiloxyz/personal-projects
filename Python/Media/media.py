#!/usr/bin/python3
# Media menu, usado para imagens, videos e audios
# Needs refactoring (Video, Audio, IMG)

from Tfuncs import gmenu

from image import Image
from audio import Audio
from video import Video


def main() -> None:
    open_menu()


def open_menu() -> None:
    img, aud, vid = Image(), Audio(), Video()
    title = "Media-Menu"
    keys = {
        "ic": (img.compress, "compress image or folder of images"),
        "if": (img.change_format, "convert image format"),
        "ocr": (img.ocr, "read image with an OCR"),
        "ac": (aud.compress, "compress audio or folder of audios"),
        "vc": (vid.compress, "compress video or folder of videos"),
    }
    gmenu(title, keys)


if __name__ == "__main__":
    main()
