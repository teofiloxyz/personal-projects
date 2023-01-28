import os
import subprocess
import shutil


class Utils:
    @staticmethod
    def run_cmd(cmd: str) -> int:
        return subprocess.call(cmd, shell=True)

    @staticmethod
    def run_cmd_and_get_output(cmd: str) -> str:
        return (
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            .stdout.decode("utf-8")
            .rstrip()
        )

    @staticmethod
    def get_user_path(path: str) -> str:
        return os.path.expanduser(path)

    @staticmethod
    def get_all_files_in_dir(dir_path: str) -> list[str]:
        return [
            os.path.join(root, file)
            for root, _, files in os.walk(dir_path)
            for file in files
        ]

    @staticmethod
    def path_join(root_path: str, appendix: str) -> str:
        return os.path.join(root_path, appendix)

    @staticmethod
    def remove_file(file: str) -> None:
        os.remove(file)

    @staticmethod
    def remove_folder(folder: str) -> None:
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def create_folder(folder: str) -> None:
        os.makedirs(folder, exist_ok=True)

    @staticmethod
    def truncate_file(file: str) -> None:
        os.truncate(file, 0)

    @staticmethod
    def create_archive(
        input_paths: list | str, output_path: str, compress: bool = True
    ) -> int:
        compress_program = (
            " --use-compress-program='xz -9T0'" if compress else ""
        )
        return subprocess.call(
            f"tar cf {output_path}{compress_program} {' '.join(input_paths)}",
            shell=True,
        )

    @staticmethod
    def check_dir_size_mb(input_dir: str) -> int:
        size = subprocess.run(
            ["du", "-m", input_dir], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        return int(size.split()[0])

    @staticmethod
    def get_oldest_file(
        input_dir: str, extension: str, reverse: bool = False
    ) -> str:
        files = {
            os.path.getmtime(os.path.join(input_dir, file)): os.path.join(
                input_dir, file
            )
            for file in os.listdir(input_dir)
            if file.endswith(extension)
        }

        return files[max(files.keys())] if reverse else files[min(files.keys())]
