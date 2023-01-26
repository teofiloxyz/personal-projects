from utils import Utils

ARCHIVE_TYPES_MAP = {
    ".tar.xz": "tar xvf",
    ".tar.gz": "tar xvzf",
    ".tar.bz2": "tar xvjf",
    ".tar.zst": "tar xvf",
    ".tar": "tar xvf",
    ".xz": "xz --decompress --keep --verbose",
    ".gz": "gunzip --decompress --keep --verbose",
    ".bz2": "bunzip2 --decompress --keep --verbose",
    ".zst": "zstd --decompress --keep --verbose",
    ".rar": "unrar x",
    ".tbz2": "tar xvjf",
    ".tgz": "tar xvzf",
    ".zip": "unzip",
    ".Z": "uncompress",
    ".7z": "7z x",
}


class Extract:
    def __init__(self, input_files: list[str]) -> None:
        self.utils = Utils()
        self.input_files = input_files

    def main(self) -> None:
        for input_file in self.input_files:
            input_file = self._get_absolute_path(input_file)
            input_name, input_ext = self._slice_input_name(input_file)
            if not self._check_if_ext_is_supported(input_ext):
                print(f"Don't know how to extract '{input_name}{input_ext}'")
                continue

            extraction_dir = self._create_extraction_dir(input_name)
            input_file_on_extraction_dir = self._move_to_extraction_dir(
                input_file, extraction_dir
            )
            self._run_extraction(
                input_file, input_file_on_extraction_dir, input_ext
            )
            self._move_from_extraction_dir(
                input_file, input_file_on_extraction_dir
            )

    def _get_absolute_path(self, input_file: str) -> str:
        if not self.utils.check_if_path_is_absolute(input_file):
            input_file = self.utils.get_abs_path_with_cwd(input_file)
        return input_file

    def _slice_input_name(self, input_file: str) -> tuple:
        """Tem mesmo que ser assim, pq splitext separa a última ext"""

        basename = self.utils.get_basename(input_file)
        if ".tar." in basename:
            return self._slice_tar_ext(basename)
        else:
            return self.utils.splitext(basename)

    def _slice_tar_ext(self, basename: str) -> tuple[str, str]:
        basename, last_ext = self.utils.splitext(basename)
        name, extension = self.utils.splitext(basename)
        extension += last_ext
        return name, extension

    def _check_if_ext_is_supported(self, extension: str) -> bool:
        if extension in ARCHIVE_TYPES_MAP.keys():
            return True
        return False

    def _create_extraction_dir(self, input_name: str) -> str:
        extraction_dir = self.utils.get_extraction_dir_path_in_cwd(input_name)
        extraction_dir = self.utils.process_output_dir_name(extraction_dir)
        self.utils.mkdir(extraction_dir)
        return extraction_dir

    def _move_to_extraction_dir(
        self, input_file: str, extraction_dir: str
    ) -> str:
        input_basename = self.utils.get_basename(input_file)
        input_file_on_extraction_dir = self.utils.join_path(
            extraction_dir, input_basename
        )

        self.utils.rename(input_file, input_file_on_extraction_dir)
        self.utils.chdir(extraction_dir)
        return input_file_on_extraction_dir

    def _run_extraction(
        self, input_file: str, input_file_on_extraction_dir: str, extension: str
    ) -> None:
        print(f"\nExtracting {input_file}")
        cmd = ARCHIVE_TYPES_MAP[extension] + " " + input_file_on_extraction_dir
        err = self.utils.run_cmd(cmd)
        if err != 0:
            print(f"Couldn't extract {input_file}")

    def _move_from_extraction_dir(
        self, input_file: str, input_file_on_extraction_dir: str
    ) -> None:
        self.utils.rename(input_file_on_extraction_dir, input_file)
        self.utils.chdir("..")
