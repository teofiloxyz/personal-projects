#!/usr/bin/python3


class Utils:
    def error(self, msg):
        subprocess.Popen(["paplay", "rejected.wav"], start_new_session=True)
        print("Error: " + msg)
        exit(1)

    def check_input(self):
        try:
            self.input = sys.argv[2]
        except IndexError:
            if self.option == "add":
                self.error("Command needs an input...")
            self.input = ""

        self.entire_folder = (
            True
            if self.option != "add" and self.input in ("", "all", "a", "al")
            else False
        )
        if not self.entire_folder:
            self.input = os.path.join(os.getcwd(), self.input)
            if self.input[-1] == "/":
                self.input = self.input[:-1]
        else:
            self.input = os.getcwd() + "/"

        if not os.path.exists(self.input):
            self.error(f"'{self.input}' does not exist...")
        self.basename = os.path.basename(self.input)
