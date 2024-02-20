"""scrape chrome extension users"""

import re

import requests
from bs4 import BeautifulSoup


class ChromeExtension:
    """scrape chome extension for user number"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"  # noqa: E501
    }

    def __init__(self, extension_id):
        self.extension_id = extension_id

    def get(self):
        """get parsed users"""
        soup = self.get_soup()
        if not soup:
            return 0

        users = self.parse_field(soup)

        return users

    def get_soup(self):
        """get the soup"""
        url = f"https://chromewebstore.google.com/detail/tubearchivist-companion/{self.extension_id}?hl=en&authuser=0"  # noqa: E501
        response = requests.get(url, headers=self.HEADERS, timeout=30)
        if not response.ok:
            print(
                f"failed to get {url}, {response.status_code} {response.text}"
            )
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        return soup

    def parse_field(self, soup):
        """extract the number"""
        char_field = soup.find("div", {"class": "F9iKBc"}).text
        users = int(re.sub(r"[^\d]+", "", char_field))

        return users
