from Tfuncs import Rofi

from utils import Utils


class Code:
    utils = Utils()
    rofi = Rofi()
    options = {"python": ("python_path", ".py"), "bash": ("bash_path", ".sh")}

    def main(self, cmd_query: str) -> None:
        divided_cmd_query = self.utils.divide_cmd_query(cmd_query, self.options)
        if not divided_cmd_query:
            return
        code_info, query = divided_cmd_query
        code_dir, extension = code_info

        files = self.get_files(code_dir, extension)
        results = {
            file: self.search_query_in_file(file, query)
            for file in files
            if len(self.search_query_in_file(file, query)) != 0
        }
        if len(results) == 0:
            self.rofi.message_box(
                f"Didn't find any line of code with '{query}'"
            )
            return

        dmenu = self.create_dmenu_with_results(results)
        choice = self.choose_with_rofi_dmenu(dmenu)
        if not choice:
            return
        file, line = self.process_choice(choice, results)
        self.open_choice_in_vim(file, line)

    def get_files(self, dir_path: str, extension: str) -> list[str]:
        cmd = f'find {dir_path} -iname "*{extension}" -print'
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def get_file_lines(self, file: str) -> list[str]:
        with open(file, "r") as f:
            return f.readlines()

    def search_query_in_file(self, file: str, query: str) -> list[tuple]:
        lines = self.get_file_lines(file)
        return [
            (n, " ".join(line.split()))
            for n, line in enumerate(lines, 1)
            if query.lower() in line.lower()
        ]

    def create_dmenu_with_results(
        self, results: dict[str, list[tuple[str, str]]]
    ) -> list[str]:
        return [
            f"{line} -> {self.utils.get_basename(file)}: {line_num}"
            for file, file_results in results.items()
            for line_num, line in file_results
        ]

    def choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open in vim"
        return self.rofi.custom_dmenu(prompt, dmenu)

    def process_choice(self, choice: str, results: dict) -> tuple[str, str]:
        line, file_basename_line_num = choice.split(" -> ")
        file_basename, line_num = file_basename_line_num.split(": ")

        for result in results.values():
            result_file_basename = self.utils.get_basename(result[1])
            result = (result[0], result_file_basename, result[2])
            if result == (line, file_basename, line_num):
                return result[1], line_num

    def open_choice_in_vim(self, file: str, line: str) -> None:
        cmd = f"alacritty -e nvim +{line} {file}"
        self.utils.run_cmd(cmd)
