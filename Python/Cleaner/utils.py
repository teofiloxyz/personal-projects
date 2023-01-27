import os
import subprocess
import shutil


class Utils:
    @staticmethod
    def move_file_or_folder(file_or_folder: str, destination: str) -> None:
        shutil.move(file_or_folder, destination)

    @staticmethod
    def copy_file_or_folder(file_or_folder: str, destination: str) -> None:
        if os.path.isdir(file_or_folder):
            shutil.copytree(file_or_folder, destination, dirs_exist_ok=True)
            return

        if os.path.isdir(destination):
            destination = os.path.join(
                destination, os.path.basename(file_or_folder)
            )
        shutil.copyfile(file_or_folder, destination)

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
    def create_archive(
        input_dir: str, output: str, compress: bool = True
    ) -> None:
        cp = " --use-compress-program='xz -9T0'" if compress else ""
        subprocess.run(f"tar cf {output}{cp} -C {input_dir} .", shell=True)

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
