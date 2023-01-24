import os
import glob
import subprocess
from datetime import datetime
from typing import Optional
from abc import abstractmethod
from enum import Enum
from dataclasses import dataclass

from database import Query, Edit
from youtube import Youtube


@dataclass
class Music:
    date: str
    title: str
    ytb_code: str
    genre: str


class ShowMode(Enum):
    ALL = "*"
    TITLES = "music_id, title"


class Playlist:
    def __init__(self) -> None:
        self.music_path = "music_dir"
        self.query_db, self.edit_db = Query(), Edit()
        self.youtube = Youtube()
        self.playlist: str

    def show(self, mode: ShowMode) -> None:
        df = self.query_db.get_music_df(self.playlist, mode.value)
        if len(df) == 0:
            print(f"{self.playlist.capitalize()} playlist is empty...")
            return
        print(df.to_string(index=False))

    def play(self, query: Optional[str] = None) -> None:
        selection = self._get_music(query)
        if not selection:
            print("Aborted...")
            return
        self._play_selection(selection)

    def _get_music(self, query: Optional[str] = None) -> Optional[list[Music]]:
        if query:
            selection = self._search_by_title(query)
        else:
            selection = self._get_selection()
        if not selection:
            return None
        return selection

    def _get_selection(self) -> Optional[list[Music]]:
        prompt = input(
            "\nls: Show titles\ng: Search by genre\n#: Select music with "
            "# ID\nPick one of the options above or leave empty to select "
            "the whole playlist\nAnything else will do a search by title: "
        )
        if prompt == "q":
            return None
        elif prompt == "":
            return self._get_all_music()
        elif prompt == "ls":
            self.show(ShowMode.TITLES)
            return self._get_selection()
        elif prompt == "g":
            return self._search_by_genre()
        else:
            return self._get_selection_by_id_or_title(prompt)

    def _get_all_music(self) -> Optional[list[Music]]:
        db_results = self.query_db.get_all_music(self.playlist, "*")
        return self._get_music_from_db_results(db_results)

    def _get_selection_by_id_or_title(
        self, query: str
    ) -> Optional[list[Music]]:
        if query.isdigit():
            db_result = self.query_db.get_music_with_id(
                self.playlist, int(query)
            )
            return self._get_music_from_db_results([db_result])
        return self._search_by_title(query)

    def _search_by_title(
        self, query: Optional[str] = None
    ) -> Optional[list[Music]]:
        if not query:
            query = input("Enter music title to search: ")
            if query == "q":
                return None

        db_results = self.query_db.get_music_with_search(
            self.playlist, "title", query
        )
        if len(db_results) == 0:
            print(f"Nothing was found with '{query}' on the title")
            return None
        print(f"Found {len(db_results)} tracks with '{query}' on the title")
        selection = self._get_music_from_db_results(db_results)
        if len(selection) == 1:
            return selection
        return self._choose_results(selection)

    def _search_by_genre(self) -> Optional[list[Music]]:
        genres = self.query_db.get_all_unique_genres(self.playlist)
        [print(f"[{n}] {genre}") for n, genre in enumerate(genres, 1)]
        prompt = input("Enter the genre number or combo (e.g: 4+2+3): ")
        selected_genres = [
            genres[int(genre) - 1]
            for genre in prompt.split("+")
            if genre.isdigit() and (int(genre) - 1) in range(len(genres))
        ]
        if not selected_genres:
            return None

        db_results = self.query_db.get_music_with_search(
            self.playlist, "genre", '%" or genre like "%'.join(selected_genres)
        )

        selected_genres = " or ".join(selected_genres)
        if len(db_results) == 0:
            print(f"Nothing was found with genre: {selected_genres}")
            return None
        print(f"Found {len(db_results)} tracks with genre: {selected_genres}")
        selection = self._get_music_from_db_results(db_results)
        if len(selection) == 1:
            return selection
        return self._choose_results(selection)

    def _choose_results(self, selection: list[Music]) -> Optional[list[Music]]:
        [print(f"[{n}] {music.title}") for n, music in enumerate(selection, 1)]
        prompt = input(
            "\nSelect one, combo (e.g: 4+2+3) or leave empty for all: "
        )
        if prompt == "q":
            return None
        elif prompt == "":
            return selection
        return [
            selection[int(choice) - 1]
            for choice in prompt.split("+")
            if choice.isdigit() and (int(choice) - 1) in range(len(selection))
        ]

    def _get_music_from_db_results(self, db_results: list) -> list[Music]:
        return [
            Music(date, title, ytb_code, genre)
            for _, date, title, ytb_code, genre in db_results
        ]

    @abstractmethod
    def _play_selection(self, selection: list[Music]) -> None:
        pass

    def _suffle_selection(self) -> bool:
        if input("\n:: Play randomly or in order? [R/o] ").lower() == "o":
            return False
        return True

    def _play_on_mpv(self, selection: list, shuffle: bool = False) -> None:
        cmd = "mpv --no-video "
        if shuffle:
            cmd += "--shuffle "
        cmd += " ".join(selection)
        subprocess.run(cmd, shell=True)

    def add(
        self, music: Optional[Music] = None, ytb_code: Optional[str] = None
    ) -> None:
        if not music:
            music = self._create_entry_to_add(ytb_code)
            if not music:
                print("Aborted...")
                return

        if self.playlist == "active":
            err = self._download_music(music)
            if err != 0:
                print("Aborted...")
                return

        db_entry = self._get_db_entry_from_music(music)
        self.edit_db.add_music(self.playlist, db_entry)
        print(f'"{music.title}" added to {self.playlist} playlist!')

    def _create_entry_to_add(self, ytb_code: Optional[str]) -> Optional[Music]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not ytb_code:
            ytb_code = self._prompt_for_ytb_code()
            if not ytb_code or not self._check_ytb_code(ytb_code):
                return None

        title = self._pick_title(ytb_code=ytb_code)
        if not title:
            return None

        genre = self._pick_genre()
        if not genre:
            return None

        return Music(now, title, ytb_code, genre)

    def _prompt_for_ytb_code(self) -> Optional[str]:
        ytb_code = input("Enter the youtube link or video code: ")
        if ytb_code == "q":
            return None
        if "/" in ytb_code:
            ytb_code = ytb_code.split("/")[-1]
        return ytb_code

    def _check_ytb_code(self, ytb_code: str) -> Optional[str]:
        if self.query_db.check_if_link_exists(self.playlist, ytb_code):
            print("Playlist already has that code...")
            return None
        return ytb_code

    def _pick_title(
        self, title: Optional[str] = None, ytb_code: Optional[str] = None
    ) -> Optional[str]:
        title = self.youtube.get_title(ytb_code) if not title else title
        if not title:
            return None
        title = self._prompt_for_title(title)
        while title in self.query_db.get_all_titles(self.playlist):
            print(f"{title} is already on the playlist...")
            title = self._prompt_for_title(title)
        return title

    def _prompt_for_title(self, title: str) -> Optional[str]:
        custom_title = input(
            "Enter custom title (artist - song) "
            f'or leave empty for "{title}": '
        )
        if custom_title == "q":
            return None
        elif custom_title != "":
            title = custom_title
        return title.replace('"', "'").replace(",", " ").replace("/", "|")

    def _pick_genre(self) -> Optional[str]:
        genres = self.query_db.get_all_unique_genres(self.playlist)
        if len(genres) == 0:
            question = "\nEnter the genre(s) (e.g.: Rock; Pop+Rock): "
        else:
            [print(f"[{n}] {genre}") for n, genre in enumerate(genres, 1)]
            question = (
                "\nEnter the genre number, or combo (e.g.: 4+2+3)\nOr "
                "enter a custom genre(s) (e.g.: Rock; Pop+Rock; 3+Pop+1): "
            )
        prompt = input(question)
        if prompt in ("q", ""):
            return None

        ans_genres = [
            genres[int(genre) - 1]
            if genre.isdigit() and (int(genre) - 1) in range(len(genres))
            else genre.capitalize()
            for genre in prompt.split("+")
        ]
        return "|".join(ans_genres)

    def _download_music(self, music: Music) -> int:
        return self.youtube.download(
            self.music_path, music.ytb_code, music.title
        )

    def _get_db_entry_from_music(self, music: Music) -> tuple:
        return music.date, music.title, music.ytb_code, music.genre

    def remove(self, music: Optional[list[Music]] = None) -> None:
        if not music:
            music = self._get_music()
            if not music:
                print("Aborted...")
                return
        [self.edit_db.remove_music(self.playlist, song.title) for song in music]
        self._archive_music(music)
        [
            print(f'"{song.title}" removed from {self.playlist} playlist!')
            for song in music
        ]

    @abstractmethod
    def _archive_music(self, music: list[Music]) -> None:
        pass

    def edit_music(self) -> None:
        music = self._get_music()
        if not music:
            print("Aborted...")
            return

        for song in music:
            option = input(f'Edit "{song.title}" [t]itle or [g]enre? ')
            if option.lower() == "t":
                self._edit_title(song)
            elif option.lower() == "g":
                self._edit_genre(song)
            else:
                print("Aborted...")
                return

    def _edit_title(self, music: Music) -> None:
        print(f"Current title: {music.title}")
        new_title = self._pick_title(title=music.title)
        if not new_title:
            print("Aborted...")
            return
        self.edit_db.update_playlist(
            self.playlist, "title", music.title, new_title
        )
        self._rename_music_file(music.title, new_title)

        print(f'Title changed from "{music.title}" to "{new_title}"')

    @abstractmethod
    def _rename_music_file(self, title: str, new_title: str) -> None:
        pass

    def _edit_genre(self, music: Music) -> None:
        print(f"Current genre: {music.genre}")
        new_genre = self._pick_genre()
        if not new_genre:
            print("Aborted...")
            return
        self.edit_db.update_playlist(
            self.playlist, "genre", music.title, new_genre
        )
        print(f'Genre changed from "{music.genre}" to "{new_genre}"')

    def export_to_csv_file(self) -> None:
        csv_output = input("Enter the ouput name of the CSV: ")
        if csv_output == "q":
            print("Aborted...")
            return
        self.query_db.export_transactions_to_csv(self.playlist, csv_output)


class Active(Playlist):
    def __init__(self) -> None:
        super().__init__()
        self.playlist = "active"

    def _play_selection(self, selection: list[Music]) -> None:
        titles = [f'"{music.title}"*' for music in selection]
        current_dir = os.getcwd()
        os.chdir(self.music_path)
        shuffle = self._suffle_selection() if len(titles) > 1 else False
        self._play_on_mpv(titles, shuffle)
        os.chdir(current_dir)

    def _archive_music(self, music: list[Music]) -> None:
        for song in music:
            self._remove_music_file(song.title)
            Archive().add(song)

    def _remove_music_file(self, title: str) -> None:
        music_file = self._find_music_file(title)
        if music_file:
            os.remove(music_file)
            return
        print(
            "WARNING! Didn't find associated music file... "
            "Assuming it's already removed..."
        )

    def _find_music_file(self, title: str) -> str:
        return glob.glob(f"{self.music_path}/{title}.*")[0]

    def _rename_music_file(self, title: str, new_title: str) -> None:
        music_file = self._find_music_file(title)
        if music_file:
            file_ext = os.path.splitext(music_file)[1]
            renamed_file = f"{self.music_path}/{new_title}{file_ext}"
            os.rename(music_file, renamed_file)


class Archive(Playlist):
    def __init__(self) -> None:
        super().__init__()
        self.playlist = "archive"

    def _play_selection(self, selection: list[Music]) -> None:
        titles = ["https://youtu.be/" + music.ytb_code for music in selection]
        shuffle = self._suffle_selection() if len(titles) > 1 else False
        self._play_on_mpv(titles, shuffle)

    def recover(self) -> None:
        music = self._get_music()
        if not music:
            print("Aborted...")
            return
        for song in music:
            Active().add(song)
            self.remove([song])
