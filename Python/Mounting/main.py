#!/usr/bin/python3
# Mounting tool for sdevs

import sys
import subprocess


class Mounting:
    def __init__(self):
        self.usb_mnt = "/mnt/usb/"
        self.m_sound = "mount.wav"
        self.d_sound = "dismount.wav"

    def main(self):
        self.check_option()
        self.process()

    def error(self, msg):
        rej_sound = "rejected.wav"
        subprocess.Popen(["paplay", rej_sound], start_new_session=True)
        print("Error: " + msg)
        exit(1)

    def check_option(self):
        self.opst_dict = {"mount": self.mount, "dismount": self.dismount}

        try:
            self.option = sys.argv[1]
        except IndexError:
            self.error("Command needs an argument: mount or dismount")

        if self.option in self.opst_dict.keys():
            self.process = self.opst_dict[self.option]
        else:
            self.error("Argument needs to be 'mount' or 'dismount'")


Mounting().main()
