"""parse and load yml"""

import os
import re

import yaml
from src.cache import clear_locks
from src.tilefy_redis import TilefyRedis


class ConfigFile:
    """represent tile.yml file"""

    TILES_CONFIG = "/data/tiles.yml"
    VALID_KEYS = [
        "background_color",
        "font_color",
        "font",
        "height",
        "humanize",
        "key_map",
        "logos",
        "plugin",
        "recreate",
        "tile_name",
        "url",
        "width",
    ]
    SEC_MAP = {
        "min": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
    }
    MIN_EXPIRE = 60

    def __init__(self):
        self.exists = os.path.exists(self.TILES_CONFIG)
        self.config_raw = False
        self.config = False

    def load_yml(self):
        """load yml into redis"""
        if not self.exists:
            print("missing tiles.yml")
            return

        self.get_conf()
        self.validate_conf()
        self.add_expire()
        self.save_config()
        clear_locks()

    def get_conf(self):
        """read config file"""
        with open(self.TILES_CONFIG, "r", encoding="utf-8") as yml_file:
            file_content = yml_file.read()
            self.config_raw = yaml.load(file_content, Loader=yaml.CLoader)

    def validate_conf(self):
        """check provided config file"""
        print(f"{self.TILES_CONFIG}: validate")
        all_tiles = self.config_raw.get("tiles")
        if not all_tiles:
            raise ValueError("missing tiles key")

        for tile_name, tile_conf in all_tiles.items():
            for tile_conf_key in tile_conf:
                if tile_conf_key not in self.VALID_KEYS:
                    message = f"{tile_name}: unexpected key {tile_conf_key}"
                    raise ValueError(message)

        self.config = self.config_raw.copy()

    def add_expire(self):
        """add expire_sec to tile_conf"""
        all_tiles = self.config.get("tiles")
        for tile_conf in all_tiles.values():
            expire = self._build_expire(tile_conf)
            tile_conf.update({"recreate_sec": expire})

    def _build_expire(self, tile_config):
        """validate config recreate return parsed secs"""
        recreate = tile_config.get("recreate", False)
        if not recreate:
            return self.SEC_MAP["d"]

        if isinstance(recreate, int):
            if recreate < self.MIN_EXPIRE:
                return self.MIN_EXPIRE

            return recreate

        if recreate == "on_demand":
            return self.MIN_EXPIRE

        try:
            value, unit = re.findall(r"[a-z]+|\d+", recreate.lower())
        except ValueError as err:
            print(f"failed to extract value and unit of {recreate}")
            raise err

        if unit not in self.SEC_MAP:
            raise ValueError(f"unit not in {self.SEC_MAP.keys()}")

        return int(value) * self.SEC_MAP.get(unit)

    def save_config(self):
        """save config in redis"""
        TilefyRedis().set_message("config", self.config)
