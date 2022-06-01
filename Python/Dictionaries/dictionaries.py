#!/usr/bin/python3

import os
import sys


class PtDefinition:
    def main(self, entry):
        print(f'A buscar a definição de: {entry}\n')
        self.url = f'https://dicionario.priberam.org/{entry}'
        if self.get_site_info() is False:
            return
        self.select_info()
        self.quit_driver()

    def get_site_info(self):
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as ec

        options = Options()
        options.headless = True  # Browser invisível
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(self.url)

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
        except Exception as exc:
            print(f'Error: {exc}')
            self.quit_driver()
            return False

    def select_info(self):
        import re

        # Processo de seleção e limpeza do string
        info_html = self.info.get_attribute('innerHTML')
        word_list = info_html.split('<span class="def">')
        for entry in word_list:
            word = entry.split('.</s')[0]
            if word[0].isupper():
                word = re.sub('<.*?>', '', word)
                print(word + ';')

        print('\nPalavras relacionadas:')
        info_html2 = self.info2.get_attribute('innerHTML')
        info_html2 = re.search('href="/(.*)</a>', info_html2).group(1)
        word_list2 = re.split('</a>', info_html2)
        for entry2 in word_list2:
            word2 = re.search('>(.*)', entry2).group(1)
            print(word2 + ';')
        print('')

    def quit_driver(self):
        self.driver.quit()
        os.remove('geckodriver.log')


class EnDefinition:
    # Public-APIs: https://github.com/public-apis/public-apis
    def main(self, entry):
        print(f'Getting definition for: {entry}\n')
        self.url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{entry}'
        if self.get_info() is False:
            return
        self.select_info()
        self.show_info()

    def get_info(self):
        import json
        import requests

        info = requests.get(self.url).text
        try:
            self.info = json.loads(info)[0]
        except KeyError:
            print('Error...')
            return False

    def select_info(self):
        meaning = self.info['meanings']
        self.part_of_speech = meaning[0]['partOfSpeech']
        self.definitions, self.synonyms, self.examples = [], [], []

        for entry in meaning[0]['definitions']:
            self.definitions.append(entry['definition'])
            if len(entry['synonyms']) != 0:
                self.synonyms.append(entry['synonyms'])
            try:
                self.examples.append(entry['example'])
            except KeyError:
                continue

    def show_info(self):
        print(f'Type: {self.part_of_speech}')
        [print(definition) for definition in self.definitions]

        if len(self.examples) != 0:
            print('Examples:')
            [print(example) for example in self.examples]

        if len(self.synonyms) != 0:
            print('Synonyms:')
            [print(synonym) for synonym in self.synonyms]
        print('')


if len(sys.argv) > 2:
    entry = ' '.join(sys.argv[2:])
    if sys.argv[1] == 'pt':
        while True:
            PtDefinition().main(entry)
            entry = input('Enter another entry to search its definition, '
                          'or quit: ')
            if entry == 'q':
                break
    elif sys.argv[1] == 'en':
        while True:
            EnDefinition().main(entry)
            entry = input('Enter another entry to search its definition, '
                          'or quit: ')
            if entry == 'q':
                break
    else:
        print('Argument error...')
else:
    print('Argument needed...')
