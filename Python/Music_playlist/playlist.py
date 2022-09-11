import os
import subprocess
from configparser import ConfigParser

from database import Database


class Playlist:
    def __init__(self, playlist: str) -> None:
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.music_path = self.config["GENERAL"]["music_path"]
        self.playlist = playlist

    def show(self, mode: str) -> None:
        selection = "*" if mode == "all" else "music_id, title"
        df = Database().Query().create_df(self.playlist, selection)
        if len(df) == 0:
            print(f"{self.playlist.capitalize()} is empty...")
            return
        print(df.to_string(index=False))

    def play(self, query: (str | None) = None) -> None:
        selection = self.SelectMusic(self.playlist).show_options(
            allow_multiple=True, query=query
        )
        if selection == "q" or len(selection) == 0:
            return
        title = selection[0]

        cmd = "mpv "
        if self.playlist == "playlist":
            selection = tuple([f'"{title}"*' for title in selection])
            os.chdir(self.music_path)
        else:
            selection = tuple(
                [
                    "https://youtu.be/"
                    + Database()
                    .Query()
                    .get_selection_with_title(self.playlist, "ytb_code", title)[
                        0
                    ]
                    for title in selection
                ]
            )
            cmd += "--no-video "
        if type(selection) is tuple and len(selection) > 1:
            if input("\n:: Play it randomly or in order? [R/o] ").lower() in (
                "",
                "r",
            ):
                cmd += "--shuffle "
        else:
            print(f"\nPlaying: {title}")
        cmd += " ".join(selection)
        subprocess.run(cmd, shell=True)

    class SelectMusic:
        def __init__(self, playlist: str) -> None:
            self.playlist = playlist

        def show_options(
            self, allow_multiple: bool = False, query: (str | None) = None
        ) -> (tuple | str):
            if query is not None:
                return self.search_by_title(query=query)
            while True:
                option = input(
                    f"\nls: Show {self.playlist} titles\n"
                    "g: Search by genre\n#: Play music with # ID\n"
                    "Pick one of the options above or leave empty "
                    f"to play the whole {self.playlist}\n"
                    "Anything else will do a search by title: "
                )
                if option == "q":
                    print("Aborted...")
                    return "q"
                elif option == "":
                    selection = Database().Query().get_all_titles(self.playlist)
                elif option == "ls":
                    Playlist(self.playlist).show("titles")
                    continue
                elif option == "g":
                    selection = self.search_by_genre()
                else:
                    try:
                        selection = (
                            Database()
                            .Query()
                            .get_title_with_id(self.playlist, int(option))
                        )
                    except ValueError:
                        selection = self.search_by_title(query=option)
                break

            if selection is None or len(selection) == 0:
                print("Got nothing...")
                return "q"

            if not allow_multiple and type(selection) is tuple:
                if len(selection) == 1:
                    selection = selection[0]
                else:
                    [
                        print(f"[{n}] {title}")
                        for n, title in enumerate(selection, 1)
                    ]
                    ans = input("Can only select one: ")
                    try:
                        selection = selection[int(ans) - 1]
                    except (ValueError, IndexError):
                        print("Aborted...")
                        return "q"
            return selection

        def search_by_title(self, query: (str | None) = None) -> (tuple | str):
            if query is None:
                query = input("Enter music title to search: ")
                if query == "q":
                    print("Aborted...")
                    return "q"

            result = (
                Database()
                .Query()
                .get_title_with_search(self.playlist, "title", query)
            )
            if len(result) == 0:
                print(f"Nothing was found with '{query}' on the title")
            elif len(result) != 1:
                [print(f"[{n}] {title}") for n, title in enumerate(result, 1)]
                selected_titles = input(
                    "Enter the title number or combo "
                    "(e.g: 2; 4+2+3) or leave empty "
                    "for all: "
                )
                if selected_titles != "":
                    selected_titles_list = []
                    for title in selected_titles.split("+"):
                        try:
                            selected_titles_list.append(result[int(title) - 1])
                        except (ValueError, IndexError):
                            print("Aborted...")
                            return "q"
                    result = tuple(selected_titles_list)
            return result

        def search_by_genre(self) -> (tuple | str):
            genres = Database().Query().get_all_genres()
            [print(f"[{n}] {genre}") for n, genre in enumerate(genres, 1)]
            selected_genres = input(
                "Enter the genre number or combo " "(e.g: 2; 4+2+3): "
            )
            selected_genres_list = []
            for genre in selected_genres.split("+"):
                try:
                    selected_genres_list.append(genres[int(genre) - 1])
                except (ValueError, IndexError):
                    print("Aborted...")
                    return "q"

            search = '%" or genre like "%'.join(selected_genres_list)
            result = (
                Database()
                .Query()
                .get_title_with_search(self.playlist, "genre", search)
            )
            selected_genres = " or ".join(selected_genres_list)
            if len(result) == 0:
                print(f"Nothing was found with genre: {selected_genres}")
            else:
                print(
                    f"Found {len(result)} tracks with genre: {selected_genres}"
                )
            return result
