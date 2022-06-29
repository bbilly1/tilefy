"""handle redis integration"""

import json
import os

import redis


class RedisBase:
    """connection base for redis"""

    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT") or 6379
    NAME_SPACE = "tl:"

    def __init__(self):
        self.conn = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT)


class TilefyRedis(RedisBase):
    """interact with redis"""

    def set_message(self, key, message, expire=False):
        """set new message"""
        self.conn.execute_command(
            "JSON.SET", self.NAME_SPACE + key, ".", json.dumps(message)
        )
        if expire:
            self.conn.execute_command("EXPIRE", self.NAME_SPACE + key, expire)

    def get_message(self, key, path="."):
        """get message from redis"""
        reply = self.conn.execute_command(
            "JSON.GET", self.NAME_SPACE + key, path
        )
        if reply:
            return json.loads(reply)

        return False

    def get_keys(self, key):
        """get list of all key matches"""
        command = f"{self.NAME_SPACE}{key}:*"
        all_keys = self.conn.execute_command("KEYS", command)

        return [i.decode().split(self.NAME_SPACE)[1] for i in all_keys]

    def del_message(self, key):
        """delete message from redis"""
        self.conn.execute_command("JSON.DEL", self.NAME_SPACE + key)
