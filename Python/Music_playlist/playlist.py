import os
import glob
import subprocess
from datetime import datetime
from typing import Optional
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
        self.playlist: str

    def show(self, mode: ShowMode) -> None:
        df = self.query_db.get_all_music(self.playlist, mode.value)
        if len(df) == 0:
            print(f"{self.playlist.capitalize()} is empty...")
            return
        print(df.to_string(index=False))

    def play(self, query: Optional[str] = None) -> None:
        selection = self.show_options(allow_multiple=True, query=query)
        if selection == "q" or len(selection) == 0:
            return
        title = selection[0]

    def _play_selection(self, selection) -> None:
        if isinstance(selection, list) and len(selection) > 1:
            shuffle = self._suffle_selection()
            self._play_on_mpv(selection, shuffle)
        else:
            self._play_on_mpv(selection)

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

        music.ytb_code = self._check_ytb_code(music.ytb_code)
        if not music.ytb_code:
            print("Aborted...")
            return None

        if self.playlist == "playlist":
            err = self._download_music(music)
            if err:
                print("Aborted...")
                return None

        self.edit_db.add_music(self.playlist, music)

    def _create_entry_to_add(self, ytb_code: Optional[str]) -> Optional[Music]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not ytb_code:
            ytb_code = self._prompt_for_ytb_code()
            return None

        title = self.pick_title(ytb_code)
        if not title:
            return None

        genre = self.pick_genre()
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

    def _download_music(self, music: Music) -> bool:
        err = Youtube().download(music.ytb_code, self.music_path, music.title)
        return err

    def remove(self, music: Optional[Music] = None) -> None:
        if not music:
            music = self._get_music()
            if not music:
                print("Aborted...")
                return
        self.edit_db.remove_music(self.playlist, music)

    def edit_music(self) -> None:
        music = self._get_music()
        if not music:
            print("Aborted...")
            return

        option = input(f'Edit "{music.title}" [t]itle or [g]enre? ')
        if option.lower() == "t":
            self._edit_title(music)
        elif option.lower() == "g":
            self._edit_genre(music)
        else:
            print("Aborted...")
            return

    def _edit_title(self, music: Music) -> None:
        print(f"Current title: {music.title}")
        new_title = self._pick_title()
        self.edit_db.update_title(self.playlist, music, new_title)
        print(f'Title changed from "{music.title}" to "{new_title}"')

    def _edit_genre(self, music: Music) -> None:
        print(f"Current genre: {music.genre}")
        new_genre = self.pick_genre()
        self.edit_db.update_genre(self.playlist, music, new_genre)
        print(f'Genre changed from "{music.genre}" to "{new_genre}"')

    def export_to_csv_file(self) -> None:
        csv_output = input("Enter the ouput name of the CSV: ")
        if csv_output == "q":
            print("Aborted...")
            return
        self.query_db.export_transactions_to_csv(self.playlist, csv_output)

    def _get_music(
        self, allow_multiple: bool = False, query: Optional[str] = None
    ) -> Optional[tuple[Music] | Music]:
        if query:
            selection = self._search_by_title(query)
        else:
            selection = self._get_selection()
        if not selection:
            return None

        if not allow_multiple and isinstance(selection, tuple):
            return self._select_one_of_results(selection)
        return selection

    def _get_selection(self) -> Optional[str]:
        prompt = input(
            f"\nls: Show {self.playlist} titles\n"
            "g: Search by genre\n#: Play music with # ID\n"
            "Pick one of the options above or leave empty "
            f"to play the whole {self.playlist}\n"
            "Anything else will do a search by title: "
        )
        if not prompt:
            return None
        elif prompt == "":
            return self.query_db.get_all_titles(self.playlist)
        elif prompt == "ls":
            self.show("titles")
            return self._get_selection()
        elif prompt == "g":
            return self._search_by_genre()
        else:
            return self._get_selection_by_id_or_title(prompt)

    def _get_selection_by_id_or_title(self, query: str) -> Optional[str]:
        try:
            return self.query_db.get_title_with_id(self.playlist, int(query))
        except ValueError:
            return self._search_by_title(query)

    def _select_one_of_results(
        self, selection: tuple[Music]
    ) -> Optional[Music]:
        [print(f"[{n}] {music.title}") for n, music in enumerate(selection, 1)]
        prompt = input("Can only select one: ")
        try:
            return selection[int(prompt) - 1]
        except (ValueError, IndexError):
            return None

    def _search_by_title(
        self, query: Optional[str] = None
    ) -> Optional[tuple[Music] | Music]:
        if not query:
            query = input("Enter music title to search: ")
            if query == "q":
                return None

        db_results = self.query_db.get_title_with_search(self.playlist, query)
        if len(db_results) == 0:
            print(f"Nothing was found with '{query}' on the title")
            return None
        print(f"Found {len(db_results)} tracks with '{query}' on title")
        return self._get_musics_from_db_results(db_results)

    def _search_by_genre(self) -> Optional[list[Music]]:
        genres = self.query_db.get_all_genres()
        [print(f"[{n}] {genre}") for n, genre in enumerate(genres, 1)]
        selected_genres = input(
            "Enter the genre number or combo (e.g: 2; 4+2+3): "
        )
        selected_genres_list = []
        for genre in selected_genres.split("+"):
            try:
                selected_genres_list.append(genres[int(genre) - 1])
            except (ValueError, IndexError):
                return None

        search = '%" or genre like "%'.join(selected_genres_list)
        db_results = self.query_db.get_title_with_search(
            self.playlist, "genre", search
        )

        selected_genres = " or ".join(selected_genres_list)
        if len(db_results) == 0:
            print(f"Nothing was found with genre: {selected_genres}")
            return None

        print(f"Found {len(db_results)} tracks with genre: {selected_genres}")
        return self._get_musics_from_db_results(db_results)

    def _get_musics_from_db_results(self, db_results: list) -> list[Music]:
        musics = []
        for result in db_results:
            date, title, ytb_code, genre = result
            musics.append(Music(date, title, ytb_code, genre))
        return musics

    def pick_title(self, title: str) -> Optional[str]:
        def prompt_for_title(title: str) -> Optional[str]:
            custom_title = input(
                "Enter custom title (artist - song) "
                f'or leave empty for "{title}": '
            )
            if custom_title == "q":
                return None
            elif custom_title != "":
                title = custom_title
            return title.replace('"', "'").replace(",", " ").replace("/", "|")

        titles = self.query_db.get_all_titles(self.playlist)
        title = prompt_for_title(title)
        while title in titles:
            print(f"{title} is already on the playlist...")
            title = prompt_for_title(title)
        return title

    def _pick_genre(self) -> Optional[str]:
        genres = self.query_db.get_all_genres()
        if len(genres) == 0:
            question = "Enter the genre(s) (e.g.: Rock; Pop+Rock): "
        else:
            [print(f"[{n}] {genre}") for n, genre in enumerate(genres, 1)]
            question = (
                "Enter the genre(s) number(s) (e.g.: 2; 4+2+3)\nOr "
                "enter a custom genre(s) (e.g.: Rock; Pop+Rock; 3+Pop+1): "
            )

        prompt = input(question)
        if prompt in ("q", ""):
            return None
        ans_list = prompt.split("+")
        ans_genres = []
        for genre in ans_list:
            try:
                ans_genres.append(genres[int(genre) - 1])
            except (ValueError, IndexError):
                # Custom genre
                ans_genres.append(genre.capitalize())
        return "|".join(ans_genres)


class Active(Playlist):
    def play(self, query: Optional[str] = None) -> None:
        super().play(query)
        selection = tuple([f'"{title}"*' for title in selection])
        os.chdir(self.music_path)
        self._play_selection(selection)

    def remove(self, music: Optional[Music] = None) -> None:
        super().remove(music)
        self._remove_music_file(music.title)
        Archive().add(music)

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

    def _edit_title(self, music: Music) -> None:
        super()._edit_title(music)
        self._rename_music_file(music.title, new_title)

    def _rename_music_file(self, title: str, new_title: str) -> None:
        music_file = self._find_music_file(title)
        if music_file:
            file_ext = os.path.splitext(music_file)[1]
            renamed_file = f"{self.music_path}/{new_title}{file_ext}"
            os.rename(music_file, renamed_file)


class Archive(Playlist):
    def play(self, query: Optional[str] = None) -> None:
        super().play(query)
        selection = tuple(
            [
                "https://youtu.be/"
                + self.query_db.get_selection_with_title(
                    self.playlist, "ytb_code", title
                )[0]
                for title in selection
            ]
        )
        self._play_selection(selection)

    def recover(self) -> None:
        music = self._get_music()
        if not music:
            print("Aborted...")
            return
        Active().add(music)
        self.remove(music)
