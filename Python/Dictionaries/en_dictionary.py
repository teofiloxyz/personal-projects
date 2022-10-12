# Public-APIs: https://github.com/public-apis/public-apis

import json
import requests


class EnDictionary:
    def __init__(self) -> None:
        self.api = API()

    def search(self, entry: str) -> str:
        api_info = self.api.get_info(entry)
        if api_info is None:
            return "Error getting info..."
        self.parse_info(api_info)
        return self.create_message(entry)

    def parse_info(self, api_info: dict) -> None:
        meanings = api_info["meanings"][0]
        self.part_of_speech = meanings["partOfSpeech"]
        self.definitions, self.synonyms, self.examples = [], [], []

        for entry in meanings["definitions"]:
            self.definitions.append(entry["definition"])
            if len(entry["synonyms"]) != 0:
                [self.synonyms.append(synonym) for synonym in entry["synonyms"]]
            try:
                self.examples.append(entry["example"])
            except KeyError:
                continue

    def create_message(self, entry: str) -> str:
        message = f"Definition of {entry}:\nType: {self.part_of_speech}\n"
        message += "\n".join(self.definitions)
        if len(self.examples) > 0:
            message += "\n\nExamples:\n" + "\n".join(self.examples)
        if len(self.synonyms) > 0:
            message += "\n\nSynonyms:\n" + "\n".join(self.synonyms)
        return message


class API:
    def get_info(self, entry: str) -> (dict | None):
        api_response = self.request_api(entry)
        return self.load_api_response(api_response)

    @staticmethod
    def request_api(entry: str) -> requests.Response:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{entry}"
        return requests.get(url)

    @staticmethod
    def load_api_response(api_response: requests.Response) -> (dict | None):
        try:
            return json.loads(api_response.text)[0]
        except KeyError:
            return None
