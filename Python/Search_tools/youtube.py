import requests
import urllib.parse
import json
from typing import Optional

from utils import Utils


class Youtube:
    utils = Utils()
    music_playlist_app = "music_playlist/main.py"
    download_path = "download_path"
    max_results = 10

    def search(self, entry: str) -> None:
        self.entry = entry
        results = self._get_search_results(entry)
        if not results:
            print("Aborted...")
            return

        self._show_results(results)
        choice = self._choose_result(results)
        if not choice:
            print("Aborted...")
            return

        ytb_link = self._get_link(choice)
        self._play(ytb_link)

    def _get_search_results(self, query: str) -> Optional[list[dict]]:
        print(f"\nSearching on youtube for '{query}':")
        return YoutubeSearch(query, max_results=self.max_results).main()

    def _show_results(self, results: list[dict]) -> None:
        for n, result in enumerate(results, 1):
            print(f'[{n}] {result["title"]}')

    def _choose_result(self, results: list[dict]) -> Optional[dict]:
        prompt = input(
            "\nChoose title or leave empty for first, "
            "anything else will search again: "
        )
        if prompt == "q":
            return None
        elif prompt == "":
            return results[0]
        elif not prompt.isdigit():
            new_results = self._get_search_results(prompt)
            if not new_results:
                return None
            self._show_results(new_results)
            return self._choose_result(new_results)
        elif 1 <= int(prompt) <= len(results):
            return results[int(prompt) - 1]

    def _get_link(self, choice: dict) -> str:
        return f'https://youtu.be/{choice["id"]}'

    def _play(self, ytb_link: str, mode: Optional[str] = None) -> None:
        cmd = f"mpv {ytb_link}"

        if not mode:
            mode = input(":: Sound, video or menu (won't close)? [S/v/m] ")
        if mode.lower() not in ("", "s", "v", "m"):
            return
        if mode.lower() in ("", "s"):
            cmd += " --no-video"
        elif mode.lower() == "m":
            self._menu(ytb_link)
            return
        self.utils.run_cmd(cmd)

    def _menu(self, ytb_link: str) -> None:
        print("\nMenu mode")
        mode = input(":: Sound or video? [S/v] ")
        if mode == "q":
            print("Aborted...")
            return
        elif mode.lower() in ("", "s"):
            self._play(ytb_link, mode="s")
        elif mode.lower() == "v":
            self._play(ytb_link, mode="v")

        prompt = input(
            "\nEnter another search or leave empty for same search"
            "\nOr [a]dd to playlist or [d]ownload: "
        )
        if prompt == "q":
            print("Aborted...")
            return
        elif prompt == "a":
            return self._add_to_playlist(ytb_link)
        elif prompt == "d":
            return self._download(ytb_link)
        elif prompt != "":
            self.entry = prompt
        return self.search(self.entry)

    def _add_to_playlist(self, ytb_link) -> None:
        cmd = f"{self.music_playlist_app} --add {ytb_link}"
        self.utils.run_cmd(cmd)

    def _download(self, ytb_link) -> None:
        cmd = (
            'yt-dlp -f "bestaudio" --continue --no-overwrites '
            "--ignore-errors --extract-audio "
            f'-o "{self.download_path}/%(title)s.%(ext)s" {ytb_link}'
        )
        self.utils.run_cmd(cmd)


class YoutubeSearch:  # youtube-search fork
    def __init__(self, search_query: str, max_results=10) -> None:
        self.search_query = search_query
        self.max_results = max_results

    def main(self) -> Optional[list]:
        BASE_URL = "https://youtube.com"
        encoded_search = urllib.parse.quote_plus(self.search_query)
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = requests.get(url).text
        while "ytInitialData" not in response:
            response = requests.get(url).text
        results = self._parse_html(response)
        if len(results) > self.max_results:
            return results[: self.max_results]
        if len(results) == 0:
            return None
        return results

    def _parse_html(self, response) -> list:
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        for contents in data["contents"]["twoColumnSearchResultsRenderer"][
            "primaryContents"
        ]["sectionListRenderer"]["contents"]:
            for video in contents["itemSectionRenderer"]["contents"]:
                res = {}
                if "videoRenderer" in video.keys():
                    video_data = video.get("videoRenderer", {})
                    res["id"] = video_data.get("videoId", None)
                    res["title"] = (
                        video_data.get("title", {})
                        .get("runs", [[{}]])[0]
                        .get("text", None)
                    )
                    res["duration"] = video_data.get("lengthText", {}).get(
                        "simpleText", 0
                    )
                    res["publish_time"] = video_data.get(
                        "publishedTimeText", {}
                    ).get("simpleText", 0)
                    results.append(res)

            if results:
                return results
        return results
