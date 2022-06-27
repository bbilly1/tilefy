"""application entry point"""

import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, render_template, send_from_directory
from src.cache import CacheManager
from src.config_parser import ConfigFile
from src.template import create_all_tiles
from src.tilefy_redis import TilefyRedis
from src.watcher import watch_yml

app = Flask(__name__)
ConfigFile().load_yml()
create_all_tiles()

scheduler = BackgroundScheduler(timezone=os.environ.get("TZ", "UTC"))
scheduler.add_job(watch_yml, "interval", seconds=5)
scheduler.start()


@app.route("/")
def home():
    """home page"""
    host_name = os.environ.get("TILEFY_HOST", "/")
    config = TilefyRedis().get_message("config")

    tiles = []
    if config:
        for tile_slug, tile_config in config["tiles"].items():
            tile_config["tile_slug"] = tile_slug
            tiles.append(tile_config)

    return render_template("home.html", tiles=tiles, host_name=host_name)


@app.route("/t/<tile_path>")
def get_tile(tile_path):
    """return tile as image"""
    tilename = os.path.splitext(tile_path)[0]

    cache_handler = CacheManager(tilename)
    if not cache_handler.tile_config:
        print(f"tile not found: {tilename}")
        return Response("tile not found", status=404)

    cache_handler.validate()

    return send_from_directory(
        directory="/data/tiles",
        path=tile_path,
        cache_timeout=60,
    )
