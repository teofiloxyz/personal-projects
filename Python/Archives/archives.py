#!/usr/bin/python3
"""Manager de arquivos (CLI): comprime, descomprime e adiciona ao arquivo,
de forma rápida, simples e organizada"""

import os
import sys
import shutil
import subprocess
from Tfuncs import oupt, qst, ffmt, fcol


class Archives:
    def main(self):
        self.check_option()
        self.check_input()
        if self.option == "add":
            self.check_input2()
        self.process()

    def check_option(self):
        self.opst_dict = {
            "extract": self.extract,
            "compress": self.compress,
            "add": self.add_to_archive,
        }
        try:
            self.option = sys.argv[1]
        except IndexError:
            self.error("Command needs options (extract, compress or add)")

        if self.option in self.opst_dict.keys():
            self.process = self.opst_dict[self.option]
        else:
            self.error(
                "First argument needs to be 'extract', " "'compress' or 'add'"
            )


Archives().main()
