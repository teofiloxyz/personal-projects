#!/usr/bin/python3
# still need refactoring!

from youtube_search import YoutubeSearch

import subprocess
import time


class Youtube:
    music_playlist = "music_playlist"
    download_path = "download_path"
    max_results = 15

    def main(self, entry: str) -> None:
        results = self.get_search_results(entry)
        self.show_results(results)
        choice_index = self.choose_result(results)
        if choice_index == 0:
            return
        link = self.get_link(results, choice_index)
        self.play(link)

    def get_search_results(self, entry: str) -> list[dict] | str:
        print(f"\nSearching on youtube for '{entry}':")
        return YoutubeSearch(entry, max_results=self.max_results).to_dict()

    def show_results(self, results: list[dict]) -> None:
        for n, result in enumerate(results, 1):
            print(f'[{n}] {result["title"]}')

    def choose_result(self, results: list) -> int:
        while True:
            prompt = input("\nChoose title or search another video: ")
            try:
                choice = int(prompt)
                if 1 <= choice <= (len(results)):
                    return choice
                else:
                    print("Wrong number!")
            except ValueError:
                if prompt == "q":
                    print("Aborted...")
                    return 0

    def get_link(self, results: list[dict], choice_index: int) -> str:
        result = results[choice_index - 1]
        return f'https://youtu.be/{result["id"]}'

    def play(self, link: str) -> None:
        while True:
            mode = input(":: Sound, video or menu (won't close)? [S/v/m] ")
            if mode == "q":
                print("Aborted...")
                return
            elif mode.lower() in ("", "s"):
                subprocess.run(["mpv", link, "--no-video"])
                return
            elif mode.lower() == "v":
                subprocess.run(["mpv", link])
                return
            elif mode.lower() == "m":
                self.menu(link)
                return

    def menu(self, link: str) -> None:
        print("\nMenu mode")
        while True:
            mode = input(":: Sound or video? [S/v] ")
            if mode == "q":
                print("Aborted...")
                return
            elif mode.lower() in ("", "s"):
                subprocess.run(["mpv", link, "--no-video"])
                break
            elif mode.lower() == "v":
                subprocess.run(["mpv", link])
                break

        menu_ans = input(
            "\nEnter another search\nOr press <enter> for same\n"
            "Or [a]dd to playlist\nOr [d]ownload: "
        )
        if menu_ans == "a":
            cmd = f"{self.music_playlist} --add {link}"
            subprocess.run(cmd, shell=True)
            time.sleep(2)

        elif menu_ans == "d":
            cmd = (
                'yt-dlp -f "bestaudio" --continue --no-overwrites '
                "--ignore-errors --extract-audio "
                f'-o "{self.download_path}/%(title)s.%(ext)s" {link}'
            )
            err = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)
            if err != 0:
                print("Error downloading...\nAborting...")
                return
            else:
                print(f"Download at {self.download_path}")
            time.sleep(2)
