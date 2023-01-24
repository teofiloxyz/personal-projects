from youtube_search import YoutubeSearch

import os
import subprocess
from typing import Optional


class Youtube:
    def get_title(self, ytb_code: str) -> Optional[str]:
        print("Getting title...")
        cmd = f"yt-dlp --get-title https://youtu.be/{ytb_code}".split()
        title = subprocess.run(cmd, capture_output=True).stdout.decode("utf-8")[
            :-1
        ]
        if title.startswith("ERROR:") or title == "":
            print("Problem getting title...\nAborting...")
            return None
        return title

    def download(
        self,
        output_dir: str,
        ytb_code: str,
        title: Optional[str] = None,
        mp3_output: bool = False,
    ) -> int:
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
        return subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)

    def download_from_txt(self) -> None:
        def get_ytb_code(entry: str) -> str:
            if "youtu" in entry and "/" in entry:
                ytb_code = entry.split("/")[-1]
            else:
                ytb_code = entry
            if len(ytb_code) != 11 or " " in ytb_code:
                search = YoutubeSearch(entry, max_results=1).to_dict()
                ytb_code = search[0]["id"]
            return ytb_code

        txt = input("Enter the txt file full path: ")
        output_dir = "path/to/output_dir"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        custom_title = None
        mp3_output = (
            True
            if input(":: Want output format to be mp3? [y/N] ").lower() == "y"
            else False
        )

        with open(str(txt), "r") as tx:
            entries = tx.readlines()
        for entry in entries:
            entry = entry.strip("\n")
            if entry.strip(" ") == "":
                continue
            ytb_code = get_ytb_code(entry)
            self.download(ytb_code, output_dir, custom_title, mp3_output)
