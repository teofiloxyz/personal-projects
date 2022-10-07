import json
import requests


class EnDictionary:
    # Public-APIs: https://github.com/public-apis/public-apis
    def main(self, entry):
        self.entry = entry
        self.message = ""
        if self.get_info():
            self.select_info()
            self.show_info()
        return self.message

    def get_info(self):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{self.entry}"
        info = requests.get(url).text
        try:
            self.info = json.loads(info)[0]
            return True
        except KeyError:
            self.message = "Error..."
            return False

    def select_info(self):
        meaning = self.info["meanings"]
        self.part_of_speech = meaning[0]["partOfSpeech"]
        self.definitions, self.synonyms, self.examples = [], [], []

        for entry in meaning[0]["definitions"]:
            self.definitions.append(entry["definition"])
            if len(entry["synonyms"]) != 0:
                [self.synonyms.append(synonym) for synonym in entry["synonyms"]]
            try:
                self.examples.append(entry["example"])
            except KeyError:
                continue

    def show_info(self):
        self.message = f"Definition of {self.entry}:"

        self.message += f"\nType: {self.part_of_speech}\n"
        self.message += "\n".join(self.definitions)

        if len(self.examples) != 0:
            self.message += "\n\nExamples:\n"
            self.message += "\n".join(self.examples)

        if len(self.synonyms) != 0:
            self.message += "\n\nSynonyms:\n"
            self.message += "\n".join(self.synonyms)
