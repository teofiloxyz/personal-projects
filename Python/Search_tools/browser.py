from utils import Utils


class Browser:
    utils = Utils()
    browser = "browser"  # firefox, chrome ...

    # Add whatever you want
    options = {
        "s": "",
        "p": "python ",
        "b": "bash ",
        "g": "golang ",
        "la": "latex ",
        "l": "linux ",
    }

    def main(self, cmd_query: str) -> None:
        divided_cmd_query = self.utils.divide_cmd_query(cmd_query, self.options)
        if not divided_cmd_query:
            return
        option, query = divided_cmd_query
        search_url = self.get_search_url(option, query)
        self.search_on_browser(search_url)

    def get_search_url(self, option: str, query: str) -> str:
        search_url = option + query
        return search_url.replace(" ", "+")

    def search_on_browser(self, search_url) -> None:
        cmd = f"{self.browser} --new-tab --url google.com/{search_url}"
        self.utils.run_cmd_on_new_shell(cmd)
