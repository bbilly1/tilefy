"""watch for changes in tiles.yml"""

import hashlib
import os

from src.scheduler_rebuild import rebuild
from src.template import create_all_tiles
from src.tilefy_redis import TilefyRedis, load_yml


class Watcher:
    """watch for changes"""

    FILE_PATH = "/data/tiles.yml"

    def __init__(self):
        self.modified = False
        self.hash = False

    def watch(self):
        """watch for changes, call from schedule"""
        modified = self.is_changed()
        if modified:
            print(f"{self.FILE_PATH}: modified")
            load_yml()
            create_all_tiles()
            self._store_last()
            rebuild()

    def is_changed(self):
        """check if file has changed"""
        self._get_modified()
        last = self._get_last()
        if not last or not self.modified:
            print("create first modified entry")
            self._get_hash()
            self._store_last()
            return False

        if self.modified == last["modified"]:
            return False

        self._get_hash()
        if self.hash != last["hash"]:
            return True

        return False

    def _get_modified(self):
        """get last modified timestamp"""
        self.modified = int(os.stat(self.FILE_PATH).st_mtime)

    def _get_hash(self):
        """get hash of file content"""
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.hash = hashlib.sha1(content.encode()).hexdigest()

    def _store_last(self):
        """store last access details in redis"""
        message = {
            "modified": self.modified,
            "hash": self.hash,
        }
        TilefyRedis().set_message("modified", message)

    def _get_last(self):
        """get last stored"""
        return TilefyRedis().get_message("modified")

    def _del_last(self):
        """remove last item from redis"""
        TilefyRedis().del_message("modified")


def watch_yml():
    """watch tiles.yml for changes"""
    Watcher().watch()
