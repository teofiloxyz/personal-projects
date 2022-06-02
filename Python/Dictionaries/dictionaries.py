#!/usr/bin/python3

import os
import sys
from Tfuncs import rofi


class PtDefinition:
    def main(self, entry):
        self.entry = entry
        self.message = ""
        if self.get_site_info():
            self.select_info()
            self.quit_driver()
        return self.message

    def get_site_info(self):
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as ec

        options = Options()
        options.headless = True  # Browser invisível
        self.driver = webdriver.Firefox(options=options)
        url = f'https://dicionario.priberam.org/{self.entry}'
        self.driver.get(url)

        # Esperar que a página carregue para copiar a informação
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'pb-main-content')))

        # Encontrar os elementos relevantes da página
        try:
            self.info = self.driver.find_element(
                By.CLASS_NAME,
                'pb-main-content').find_element(By.ID, 'resultados')
            self.info2 = self.driver.find_element(
                By.CLASS_NAME, 'pb-main-content').find_element(
                    By.CLASS_NAME, 'pb-relacionadas-results')
            return True
        except Exception as exc:
            self.message = f'Error: {exc}'
            self.quit_driver()
            return False

    def select_info(self):
        import re

        self.message = f'Definição de {self.entry}:\n'

        # Processo de seleção e limpeza do string
        info_html = self.info.get_attribute('innerHTML')
        word_list = info_html.split('<span class="def">')
        for entry in word_list:
            word = entry.split('.</s')[0]
            if word[0].isupper():
                word = re.sub('<.*?>', '', word)
                self.message += word + ';\n'

        self.message += '\nPalavras relacionadas:\n'
        info_html2 = self.info2.get_attribute('innerHTML')
        info_html2 = re.search('href="/(.*)</a>', info_html2).group(1)
        word_list2 = re.split('</a>', info_html2)
        for entry2 in word_list2:
            word2 = re.search('>(.*)', entry2).group(1)
            self.message += word2 + ';\n'

    def quit_driver(self):
        self.driver.quit()
        os.remove('geckodriver.log')


class EnDefinition:
    # Public-APIs: https://github.com/public-apis/public-apis
    def main(self, entry):
        self.entry = entry
        self.message = ""
        if self.get_info():
            self.select_info()
            self.show_info()
        return self.message

    def get_info(self):
        import json
        import requests

        url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{self.entry}'
        info = requests.get(url).text
        try:
            self.info = json.loads(info)[0]
            return True
        except KeyError:
            self.message = 'Error...'
            return False

    def select_info(self):
        meaning = self.info['meanings']
        self.part_of_speech = meaning[0]['partOfSpeech']
        self.definitions, self.synonyms, self.examples = [], [], []

        for entry in meaning[0]['definitions']:
            self.definitions.append(entry['definition'])
            if len(entry['synonyms']) != 0:
                [self.synonyms.append(synonym)
                 for synonym in entry['synonyms']]
            try:
                self.examples.append(entry['example'])
            except KeyError:
                continue

    def show_info(self):
        self.message = f"Definition of {self.entry}:"

        self.message += f'\nType: {self.part_of_speech}\n'
        self.message += "\n".join(self.definitions)

        if len(self.examples) != 0:
            self.message += '\n\nExamples:\n'
            self.message += "\n".join(self.examples)

        if len(self.synonyms) != 0:
            self.message += '\n\nSynonyms:\n'
            self.message += "\n".join(self.synonyms)


def general_loop(func, entry):
    while True:
        message = func.main(entry)
        prompt = 'Enter another entry to search its definition, or quit'
        entry = rofi.simple_prompt(prompt, message)
        if entry == 'q':
            return


if len(sys.argv) > 2:
    entry = ' '.join(sys.argv[2:])
    if sys.argv[1] == 'pt':
        func = PtDefinition()
    elif sys.argv[1] == 'en':
        func = EnDefinition()
    else:
        print('Argument error...')
        exit(1)
    general_loop(func, entry)
else:
    print('Argument needed...')
    exit(1)
