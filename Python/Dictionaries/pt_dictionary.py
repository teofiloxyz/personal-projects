from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

import os
import re


class PtDictionary:
    def __init__(self) -> None:
        self.webdriver = WebDriver()

    def search(self, entry: str) -> str:
        webdriver_respose = self.webdriver.get_site_info(entry)
        if type(webdriver_respose) is str:
            return webdriver_respose
        parsed_info = self.parse_info(webdriver_respose)  # Ignore err
        return self.create_message(entry, parsed_info)

    def get_info(self, entry: str) -> tuple | str:
        return self.webdriver.get_site_info(entry)

    def parse_info(self, webdriver_respose: tuple) -> tuple:
        info_main, info_appendix = webdriver_respose
        definitions, related_words = [], []

        word_list = info_main.split('<span class="def">')
        for entry in word_list:
            word = entry.split(".</s")[0]
            if word[0].isupper():
                definitions.append(re.sub("<.*?>", "", word))

        info_appendix = re.search('href="/(.*)</a>', info_appendix).group(1)
        word_list2 = re.split("</a>", info_appendix)
        for entry2 in word_list2:
            related_words.append(re.search(">(.*)", entry2).group(1))

        return definitions, related_words

    def create_message(self, entry: str, parsed_info: tuple) -> str:
        definitions, related_words = parsed_info

        message = f"Definição de {entry}:\n"
        for dfn in definitions:
            message += f"{dfn};\n"

        message += "\nPalavras relacionadas:\n"
        for rw in related_words:
            message += f"{rw};\n"

        return message


class WebDriver:
    def __init__(self) -> None:
        options = Options()
        options.headless = True  # Browser invisível
        self.driver = webdriver.Firefox(options=options)

    def get_site_info(self, entry: str) -> tuple | str:
        url = f"https://dicionario.priberam.org/{entry}"
        self.driver.get(url)

        # Esperar que a página carregue para copiar a informação
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "pb-main-content")
            )
        )

        # Encontrar os elementos relevantes da página
        try:
            info_main = self.driver.find_element(
                By.CLASS_NAME, "pb-main-content"
            ).find_element(By.ID, "resultados")
            info_appendix = self.driver.find_element(
                By.CLASS_NAME, "pb-main-content"
            ).find_element(By.CLASS_NAME, "pb-relacionadas-results")
        except Exception as exc:
            self.quit_driver()
            return f"Error: {exc}"

        info_main = info_main.get_attribute("innerHTML")
        info_appendix = info_appendix.get_attribute("innerHTML")
        self.quit_driver()
        return info_main, info_appendix

    def quit_driver(self) -> None:
        self.driver.quit()
        os.remove("geckodriver.log")
