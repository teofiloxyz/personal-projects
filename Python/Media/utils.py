import os
import subprocess


class Utils:
    def run_cmd(self, cmd: str) -> int:
        return subprocess.call(cmd, shell=True)

    def get_input(
        self, file_exts: tuple, only_one_file: bool = False
    ) -> list[dict]:
        prompt = input("Enter the file or folder of files path: ")
        if os.path.isdir(prompt) and not only_one_file:
            return [
                {"input": os.path.join(prompt, file)}
                for file in os.listdir(prompt)
                if file.endswith(file_exts)
            ]
        elif os.path.isfile(prompt):
            if prompt.endswith(file_exts):
                return [{"input": prompt}]
            else:
                print(f"Accepted formats are: {'; '.join(file_exts)}")
        return []

    def create_output_dir(
        self, files: list[dict], title: str = "Compressed"
    ) -> str:
        input_dir = os.path.dirname(files[0]["input"])
        output_dir = os.path.join(input_dir, title)
        while os.path.isdir(output_dir):
            output_dir += "_"
        os.mkdir(output_dir)
        return output_dir

    def get_output(
        self, files: list[dict], output_dir: str, output_ext: str
    ) -> list[dict]:
        for file in files:
            input_basename = os.path.basename(file["input"])
            basename_no_ext = os.path.splitext(input_basename)[0]
            output_basename = basename_no_ext + "." + output_ext
            output_path = os.path.join(output_dir, output_basename)
            file["output"] = output_path
        return files

    def get_output_alternate_ext(
        self, files: list[dict], output_dir: str
    ) -> list[dict]:
        # incorporate this in get_output func
        for file in files:
            input_basename = os.path.basename(file["input"])
            basename_no_ext, input_ext = os.path.splitext(input_basename)
            output_ext = "png" if input_ext == ".jpg" else "jpg"
            output_basename = basename_no_ext + "." + output_ext
            output_path = os.path.join(output_dir, output_basename)
            file["output"] = output_path
        return files

    def concatenate(self) -> bool:
        prompt = input(":: Do you want to concatenate the files? [y/N] ")
        if prompt.lower() == "y":
            return True
        return False

    def get_concatenation(self, files: list[dict]) -> dict:
        # Needs rework
        output = files[0]["output"]
        file_dir = os.path.dirname(files[0]["input"])
        txt_file = os.path.join(file_dir, "input_files.txt")

        with open(txt_file, "w") as txt:
            for file in files:
                entry = f'file \'{file["input"]}\''
                txt.write(entry + "\n")
                print(entry)

        prompt = input(":: Edit the list of files to be concatenated? [y/N] ")
        if prompt.lower() == "y":
            self.open_on_vim(txt_file)
        return {"input": txt_file, "output": output}

    def open_on_vim(self, txt_file: str) -> None:
        cmd = f'nvim "{txt_file}"'
        subprocess.run(cmd, shell=True)
