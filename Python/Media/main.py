#!/usr/bin/python3
# Media menu, usado para imagens, videos e audios

from Tfuncs import Menu

from image import Image
from audio import Audio
from video import Video


def main() -> None:
    img, aud, vid = Image(), Audio(), Video()
    menu = Menu(title="Media-Menu")

    menu.add_option(
        key="ic", func=img.compress, help="compress image or folder of images"
    )
    menu.add_option(key="if", func=img.convert, help="convert image format")
    menu.add_option(key="ocr", func=img.ocr, help="read image with an OCR")
    menu.add_option(
        key="ac", func=aud.compress, help="compress audio or folder of audios"
    )
    menu.add_option(
        key="vc", func=vid.compress, help="compress video or folder of videos"
    )

    menu.start()


if __name__ == "__main__":
    main()
