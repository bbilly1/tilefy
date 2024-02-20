"""make api call to get variable text"""

import requests
from src.plugins.chrome_extension import ChromeExtension


def humanize(number):
    """humanize number to string"""

    break_points = [
        (999999999, "B"),
        (999999, "M"),
        (999, "K"),
    ]

    for break_point in break_points:
        break_nr, break_str = break_point
        if number > break_nr:
            return f"{round(number / (break_nr + 1), 1)}{break_str}"

    return str(number)


class Api:
    """make request and parse"""

    def __init__(self, tile_config):
        self.tile_config = tile_config

    def get_text(self):
        """run all"""
        if "plugin" in self.tile_config:
            key_match = self.plugin()
        else:
            key_match = self.url()

        to_humanize = self.tile_config.get("humanize", True)
        if not to_humanize or isinstance(key_match, str):
            return str(key_match)

        return humanize(key_match)

    def url(self):
        """make call using url from tile_config"""
        response = self.make_request()
        key_match = self.walk_response(response)
        if not key_match and not key_match == 0:
            print(f"failed to result with key_map: {response}")
            raise ValueError

        return key_match

    def make_request(self):
        """make request"""
        url = self.tile_config["url"]
        response = requests.get(url, timeout=2)
        if not response.ok:
            print(f"failed to make request: {url}")
            raise ValueError

        return response.json()

    def walk_response(self, response):
        """walk response dict for key"""
        for item in self.tile_config["key_map"]:
            response = response[item]

        return response

    def plugin(self):
        """make request with plugin"""
        plugin_name = self.tile_config["plugin"]["name"]
        item_id = self.tile_config["plugin"]["id"]
        if plugin_name == "chrome-extension-users":
            users = ChromeExtension(item_id).get()
            return users

        raise ValueError("missing plugin")
