"""configure scheduled jobs"""

from redis.connection import ResponseError
from src.template import create_single_tile
from src.tilefy_redis import TilefyRedis


class CacheManager:
    """handle rebuild cache for tiles"""

    SEC_MAP = {
        "min": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
    }

    def __init__(self, tilename):
        self.tilename = tilename
        self.tile_config = self.get_tile_config()

    def get_tile_config(self):
        """get conf from redis"""
        path = f"tiles.{self.tilename}"
        try:
            tile_config = TilefyRedis().get_message("config", path=path)
        except ResponseError:
            tile_config = False

        return tile_config

    def validate(self):
        """validate cache"""
        key = f"lock:{self.tilename}"
        use_cached = TilefyRedis().get_message(key)
        if use_cached:
            print(f"{self.tilename}: use cached tile")
            return

        create_single_tile(self.tilename, self.tile_config)


def clear_locks():
    """clear all locks from redis"""
    _redis = TilefyRedis()
    all_locks = _redis.get_keys("lock")
    for lock in all_locks:
        _redis.del_message(lock)
