from Tfuncs import Rofi

from dataclasses import dataclass

from utils import Utils


@dataclass
class Result:
    path: str
    rofi_line: str
    line_num: int
    keyword_count: int


class Notes:
    ROFI_MAX_LINE_SPACE = 93

    def __init__(self, notes_dir: str) -> None:
        self.utils = Utils()
        self.rofi = Rofi()
        self.notes_dir = notes_dir

    def search(self, query: str) -> None:
        """
        Counts how many query keywords are present in the path and in
        each line of the file. Then combines the keywords found in the lines
        with any keywords from the corresponding file path, and counts the
        unique keywords. Finally, sorts the results by the keyword count.
        """

        query_words = query.lower().split()
        files = self._get_all_notes_files()
        results = []
        for file in files:
            file_keywords = self._get_keywords_on_str(query_words, file)
            file_keyword_count = len(file_keywords)
            if file_keyword_count > 0:
                result = self._create_result(file, file_keyword_count)
                results.append(result)

            lines = self._get_lines_of_file(file)
            for line_num, line in enumerate(lines, 1):
                line = line.strip("\n")
                line_keywords = self._get_keywords_on_str(query_words, line)
                line_keyword_count = len(line_keywords)
                if line_keyword_count == 0:
                    continue
                line_plus_file_keywords = file_keywords | line_keywords
                line_plus_file_keyword_count = len(line_plus_file_keywords)
                result = self._create_result(
                    file, line_plus_file_keyword_count, line_num
                )
                results.append(result)

        if len(results) == 0:
            query = "' or '".join(query.split())
            self.rofi.message_box(
                f"Didn't find within {self.notes_dir} anything with '{query}'"
            )
            return
        elif len(results) == 1:
            choice = results[0]
        else:
            results = self._sort_results(results)
            dmenu = [result.rofi_line for result in results]
            dmenu_choice = self._choose_with_rofi_dmenu(dmenu)
            if dmenu_choice == "":
                return
            choice = results[dmenu.index(dmenu_choice)]
        self._open_choice_with_vim(choice)

    def _get_all_notes_files(self) -> list[str]:
        cmd = f"find {self.notes_dir} -type f"
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def _get_keywords_on_str(
        self, query_words: list[str], path_or_line: str
    ) -> set[str]:
        return {
            word for word in query_words if word.lower() in path_or_line.lower()
        }

    def _create_result(
        self, path: str, keyword_count: int, line_num: int = 0
    ) -> Result:
        split_path = path.split("/")
        name = split_path[-1]
        last_two_dirs = "/".join(split_path[-3:-1])
        caracters_space = len(name + str(line_num)) + 5 + len(last_two_dirs)
        remaining_space = self.ROFI_MAX_LINE_SPACE - caracters_space
        whitespace = " " * remaining_space
        rofi_line = f"{name}:{line_num}{whitespace}.../{last_two_dirs}"

        return Result(path, rofi_line, line_num, keyword_count)

    def _get_lines_of_file(self, file: str) -> list[str]:
        with open(file, "r") as f:
            return f.readlines()

    def _sort_results(self, results: list[Result]) -> list[Result]:
        return sorted(results, key=self._get_keyword_count, reverse=True)

    def _get_keyword_count(self, result: Result) -> int:
        return result.keyword_count

    def _choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open with vim: "
        return self.rofi.custom_dmenu(prompt, dmenu)

    def _open_choice_with_vim(self, choice: Result) -> None:
        cmd = f'alacritty -e nvim +{choice.line_num} "{choice.path}"'
        self.utils.run_cmd(cmd)
