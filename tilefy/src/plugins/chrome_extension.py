"""scrape chrome extension users"""

import re

import requests
from bs4 import BeautifulSoup


class ChromeExtension:
    """scrape chome extension for user number"""

    def __init__(self, extension_id):
        self.extension_id = extension_id

    def get(self):
        """get parsed users"""
        soup = self.get_soup()
        users = self.parse_field(soup)

        return users

    def get_soup(self):
        """get the soup"""
        url = (
            "https://chrome.google.com/webstore/detail/"
            + f"{self.extension_id}?hl=en&authuser=0"
        )
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")

        return soup

    def parse_field(self, soup):
        """extract the number"""
        char_field = soup.find("span", {"class": "e-f-ih"}).text
        users = int(re.sub(r"[^\d]+", "", char_field))

        return users
