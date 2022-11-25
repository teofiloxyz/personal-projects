#!/usr/bin/python3
# Media menu, usado para imagens, videos e audios

import os
import subprocess
from Tfuncs import gmenu, inpt, oupt


class Media:
    def __init__(self):
        self.img_exts = "jpg", "png"
        self.vid_exts = "mp4", "avi", "m4v", "mov"
        self.aud_exts = "mp3", "m4b", "opus", "wav"


med = Media()
title = "Media-Menu"
keys = {
    "ic": (med.compress_img, "compress image or folder of images"),
    "if": (med.change_img_format, "convert image format"),
    "ocr": (med.ocr, "read image with an OCR"),
    "vc": (med.compress_vid, "compress video or folder of videos"),
    "ac": (med.compress_aud, "compress audio or folder of audios"),
}
gmenu(title, keys)
