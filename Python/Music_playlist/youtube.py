import subprocess


class Youtube:
    @staticmethod
    def get_title(ytb_code: str) -> str:
        print("Getting title...")
        cmd = f"yt-dlp --get-title https://youtu.be/{ytb_code}".split()
        title = subprocess.run(cmd, capture_output=True).stdout.decode("utf-8")[
            :-1
        ]
        if title.startswith("ERROR:") or title == "":
            print("Problem getting title...\nAborting...")
            return "q"
        return title

    def download(
        self,
        ytb_code: str,
        output_dir: str,
        title: (str | None) = None,
        mp3_output: bool = False,
    ) -> (int | None):
        print("Downloading...")
        if title is None:
            output_path = f"{output_dir}/%(title)s.%(ext)s"
        else:
            output_path = f"{output_dir}/{title}.%(ext)s"
        cmd = (
            'yt-dlp -f "bestaudio" --continue --no-overwrites '
            "--ignore-errors --extract-audio -o "
            f'"{output_path}" https://youtu.be/{ytb_code}'
        )
        if mp3_output:
            cmd += " --audio-format mp3"
        err = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)
        if err != 0:
            print("Error downloading...\nAborting...")
            return err
