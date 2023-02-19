# Search file or folder by title

from Tfuncs import Rofi

from utils import Utils


class Paths:
    ROFI_MAX_LINE_SPACE = 93

    def __init__(self, search_dir: str) -> None:
        self.utils = Utils()
        self.rofi = Rofi()
        self.search_dir = search_dir

    def search(self, query: str) -> None:
        results = self._find_paths(query)
        if len(results) == 1 and results[0] == "":
            query = "' and '".join(query.split())
            self.rofi.message_box(
                f"Didn't find within {self.search_dir} any path with '{query}'"
            )
            return
        if len(results) == 1:
            choice = results[0]
        else:
            results = self._sort_results_by_mtime(results)
            dmenu = self._clean_results(results)
            dmenu_choice = self._choose_with_rofi_dmenu(dmenu)
            if dmenu_choice == "":
                return
            choice = results[dmenu.index(dmenu_choice)]
        self._open_choice_with_ranger(choice)

    def _find_paths(self, query: str) -> list[str]:
        cmd = self._get_right_cmd(query)
        output = self.utils.run_cmd_and_get_output(cmd)
        return output.split("\n")

    def _get_right_cmd(self, query: str) -> str:
        """If the search_dir tree is large, it uses plocate instead of find"""

        if self.search_dir.count("/") > 2:
            pattern_args = [
                '-ipath "*{}*"'.format(part) for part in query.split()
            ]
            return f'find {self.search_dir} {" ".join(pattern_args)}'
        pattern_args = ['-e "*{}*"'.format(part) for part in query.split()]
        return f'plocate -i "{self.search_dir}" {" ".join(pattern_args)}'

    def _sort_results_by_mtime(self, results: list) -> list:
        return sorted(
            results, key=self.utils.get_modification_time, reverse=True
        )

    def _clean_results(self, results: list) -> list:
        dmenu = []
        for path in results:
            split_path = path.split("/")
            name = split_path[-1]
            last_three_dirs = "/".join(split_path[-4:-1])
            caracters_space = len(name) + 4 + len(last_three_dirs)
            remaining_space = self.ROFI_MAX_LINE_SPACE - caracters_space
            whitespace = " " * remaining_space
            dmenu.append(f"{name}{whitespace}.../{last_three_dirs}")
        return dmenu

    def _choose_with_rofi_dmenu(self, dmenu: list) -> str:
        prompt = "Choose which one to open with ranger: "
        return self.rofi.custom_dmenu(prompt, dmenu)

    def _open_choice_with_ranger(self, path: str) -> None:
        cmd = f'alacritty -e ranger "{path}"'
        self.utils.run_cmd(cmd)
