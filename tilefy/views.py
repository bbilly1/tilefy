"""application entry point"""

import os

from flask import Flask, render_template, send_from_directory
from src.scheduler import TilefyScheduler
from src.template import create_all_tiles, create_single_tile
from src.tilefy_redis import TilefyRedis, load_yml

app = Flask(__name__)

load_yml()
TilefyScheduler().setup_schedule()
create_all_tiles()


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
    tile_config = TilefyRedis().get_message("config", path=f"tiles.{tilename}")
    recreate = tile_config.get("recreate")
    if recreate == "on_demand":
        create_single_tile(tilename, tile_config)

    return send_from_directory(
        directory="/data/tiles",
        path=tile_path,
        cache_timeout=100,
    )
