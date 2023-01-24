import os
import subprocess
import requests
import urllib.parse
import json
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
                search = YoutubeSearch(entry, max_results=1).main()
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


class YoutubeSearch:  # youtube-search fork
    def __init__(self, search_query: str, max_results=10) -> None:
        self.search_query = search_query
        self.max_results = max_results

    def main(self) -> list:
        BASE_URL = "https://youtube.com"
        encoded_search = urllib.parse.quote_plus(self.search_query)
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = requests.get(url).text
        while "ytInitialData" not in response:
            response = requests.get(url).text
        results = self._parse_html(response)
        if len(results) > self.max_results:
            return results[: self.max_results]
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
