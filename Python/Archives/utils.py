#!/usr/bin/python3

import os
import subprocess


class Utils:
    def error(self, msg):
        subprocess.Popen(["paplay", "rejected.wav"], start_new_session=True)
        print("Error: " + msg)
        exit(1)

    def check_input(self, input_file_or_dir) -> bool:
        if os.path.isdir(input_file_or_dir):
            return True
        return False
