from Tfuncs import Rofi

from dataclasses import dataclass

from utils import Utils


@dataclass
class Result:
    path: str
    rofi_line: str
    line_num: int


class Code:
    ROFI_MAX_LINE_SPACE = 93

    def __init__(self, code_dir: str) -> None:
        self.utils = Utils()
        self.rofi = Rofi()
        self.code_dir = code_dir

    def search(self, query: str, file_extension: str) -> None:
        files = self._get_all_code_files(file_extension)
        results = []
        for file in files:
            lines = self._get_lines_of_file(file)
            for line_num, line in enumerate(lines, 1):
                line = line.strip("\n")
                if query.lower() not in line.lower():
                    continue
                result = self._create_result(file, line_num)
                results.append(result)

        if len(results) == 0:
            self.rofi.message_box(
                f"Didn't find within {self.code_dir} "
                f"any line of code with '{query}'"
            )
            return
        elif len(results) == 1:
            choice = results[0]
        else:
            dmenu = [result.rofi_line for result in results]
            dmenu_choice = self._choose_with_rofi_dmenu(dmenu)
            if dmenu_choice == "":
                return
            choice = results[dmenu.index(dmenu_choice)]
        self._open_choice_with_vim(choice)

    def _get_all_code_files(self, file_extension: str) -> list[str]:
        cmd = f'find {self.code_dir} -type f -iname "*{file_extension}"'
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def _get_lines_of_file(self, file: str) -> list[str]:
        with open(file, "r") as f:
            return f.readlines()

    def _create_result(self, path: str, line_num: int) -> Result:
        split_path = path.split("/")
        name = split_path[-1]
        last_two_dirs = "/".join(split_path[-3:-1])
        caracters_space = len(name + str(line_num)) + 5 + len(last_two_dirs)
        remaining_space = self.ROFI_MAX_LINE_SPACE - caracters_space
        whitespace = " " * remaining_space
        rofi_line = f"{name}:{line_num}{whitespace}.../{last_two_dirs}"

        return Result(path, rofi_line, line_num)

    def _choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open with vim: "
        return self.rofi.custom_dmenu(prompt, dmenu)

    def _open_choice_with_vim(self, choice: Result) -> None:
        cmd = f'alacritty -e nvim +{choice.line_num} "{choice.path}"'
        self.utils.run_cmd(cmd)
