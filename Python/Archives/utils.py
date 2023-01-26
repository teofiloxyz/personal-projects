import os
import subprocess


class Utils:
    @staticmethod
    def run_cmd(cmd: str) -> int:
        return subprocess.call(cmd, shell=True)

    @staticmethod
    def check_if_is_dir(path: str) -> bool:
        if os.path.isdir(path):
            return True
        return False

    @staticmethod
    def check_if_path_is_absolute(path: str) -> bool:
        return os.path.isabs(path)

    @staticmethod
    def get_abs_path_with_cwd(path: str) -> str:
        cwd = os.getcwd()
        return os.path.join(cwd, path)

    @staticmethod
    def chdir(path: str) -> None:
        os.chdir(path)

    @staticmethod
    def mkdir(dir_path: str) -> None:
        os.mkdir(dir_path)

    @staticmethod
    def rename(path: str, new_path: str) -> None:
        os.rename(path, new_path)

    @staticmethod
    def join_path(base_path: str, ext_path: str) -> str:
        return os.path.join(base_path, ext_path)

    @staticmethod
    def get_basename(path: str) -> str:
        return os.path.basename(path)

    @staticmethod
    def splitext(basename: str) -> tuple[str, str]:
        return os.path.splitext(basename)

    @staticmethod
    def get_output_name_in_cwd(input_files: list) -> str:
        cwd = os.getcwd()
        if len(input_files) == 1:
            basename = os.path.basename(input_files[0])
            return os.path.join(cwd, basename)
        return os.path.join(cwd, "Compressed")

    @staticmethod
    def get_extraction_dir_path_in_cwd(input_name: str) -> str:
        return os.path.join(os.getcwd(), "Extracted_" + input_name)

    @staticmethod
    def get_dir_contents(dir_path: str) -> list[str]:
        return [os.path.join(dir_path, file) for file in os.listdir(dir_path)]

    @staticmethod
    def process_output_file_name(output_file: str) -> str:
        if os.path.exists(output_file):
            i = 1
            output_file_noext, file_ext = os.path.splitext(output_file)
            while os.path.exists(f"{output_file_noext}_{i}{file_ext}"):
                i += 1
            output_file = f"{output_file_noext}_{i}{file_ext}"
        return output_file

    @staticmethod
    def process_output_dir_name(output_dir: str) -> str:
        if os.path.exists(output_dir):
            i = 1
            while os.path.exists(f"{output_dir}_{i}"):
                i += 1
            output_dir = f"{output_dir}_{i}"
        return output_dir
