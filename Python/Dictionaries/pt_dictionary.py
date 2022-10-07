from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import os
import re


class PtDictionary:
    def main(self, entry):
        self.entry = entry
        self.message = ""
        if self.get_site_info():
            self.select_info()
            self.quit_driver()
        return self.message

    def get_site_info(self):
        options = Options()
        options.headless = True  # Browser invisível
        self.driver = webdriver.Firefox(options=options)
        url = f"https://dicionario.priberam.org/{self.entry}"
        self.driver.get(url)

        # Esperar que a página carregue para copiar a informação
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "pb-main-content"))
        )

        # Encontrar os elementos relevantes da página
        try:
            self.info = self.driver.find_element(
                By.CLASS_NAME, "pb-main-content"
            ).find_element(By.ID, "resultados")
            self.info2 = self.driver.find_element(
                By.CLASS_NAME, "pb-main-content"
            ).find_element(By.CLASS_NAME, "pb-relacionadas-results")
            return True
        except Exception as exc:
            self.message = f"Error: {exc}"
            self.quit_driver()
            return False

    def select_info(self):
        self.message = f"Definição de {self.entry}:\n"

        # Processo de seleção e limpeza do string
        info_html = self.info.get_attribute("innerHTML")
        word_list = info_html.split('<span class="def">')
        for entry in word_list:
            word = entry.split(".</s")[0]
            if word[0].isupper():
                word = re.sub("<.*?>", "", word)
                self.message += word + ";\n"

        self.message += "\nPalavras relacionadas:\n"
        info_html2 = self.info2.get_attribute("innerHTML")
        info_html2 = re.search('href="/(.*)</a>', info_html2).group(1)
        word_list2 = re.split("</a>", info_html2)
        for entry2 in word_list2:
            word2 = re.search(">(.*)", entry2).group(1)
            self.message += word2 + ";\n"

    def quit_driver(self):
        self.driver.quit()
        os.remove("geckodriver.log")
