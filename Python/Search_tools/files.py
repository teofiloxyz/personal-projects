# Search file or folder by title

from Tfuncs import Rofi

from utils import Utils


class Files:
    utils = Utils()
    rofi = Rofi()
    dir_path = "/home"

    def main(self, entry: str) -> None:
        results = self.search_entry(entry)
        if len(results) == 0:
            self.rofi.message_box(
                f"Didn't find in home any file with '{entry}'"
            )
            return
        choice = self.choose_with_rofi_dmenu(results)
        if choice != "":
            self.open_choice_with_ranger(choice)

    def search_entry(self, entry: str) -> list[str]:
        cmd = f'find {self.dir_path} -iname ".*{entry}*"'
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def choose_with_rofi_dmenu(self, results: list) -> str:
        prompt = "Choose which one to open with ranger"
        return self.rofi.custom_dmenu(prompt, results)

    def open_choice_with_ranger(self, path: str) -> None:
        cmd = "alacritty -e ranger "
        if self.utils.check_if_is_dir(path):
            cmd += "--selectfile=" + path
        else:
            cmd += path
        self.utils.run_cmd(cmd)
