"""create from template"""

from datetime import datetime
from os import path

from PIL import Image, ImageDraw, ImageFont
from src.api_call import Api
from src.tilefy_redis import TilefyRedis


class TileImage:
    """interact with tile object"""

    TILE_BASE = "/data/tiles"
    FONT_DEFAULT = "/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf"

    def __init__(self, tile_slug, tile_config):
        self.tile_slug = tile_slug
        self.tile_config = tile_config
        self.content_height = self.tile_config["height"] // 3 * 2
        self.img = False

    def build_tile(self):
        """create the tile"""
        print(f"{self.tile_slug}: {self.tile_config}")
        self.create_background()
        right = self.add_logos()
        self.add_text(right)
        self.save_tile()

    def create_background(self):
        """create the background"""
        size = (self.tile_config["width"], self.tile_config["height"])
        color = self.tile_config["background_color"]
        self.img = Image.new(mode="RGBA", size=size, color=color)

    def _get_logo(self, logo_path):
        """return logo pillow object"""
        if logo_path.startswith("logos/"):
            # custom logo
            file_path = path.join("/data", logo_path)
        else:
            # default logo
            file_path = path.join("logos", logo_path)

        logo = Image.open(file_path)
        logo.thumbnail((self.content_height, self.content_height))

        return logo.convert("RGBA")

    def add_logos(self):
        """add logos to img"""
        logo_paths = self.tile_config["logos"]
        if not logo_paths:
            return False

        top = (self.tile_config["height"] - self.content_height) // 2
        for idx, logo_path in enumerate(logo_paths):
            logo = self._get_logo(logo_path)
            left = top + self.content_height * idx
            right = left + self.content_height
            self.img.alpha_composite(logo, dest=(left, top))

        return right

    def add_text(self, right):
        """write text on tile"""
        draw = ImageDraw.Draw(self.img)
        # font
        font_color = self.tile_config["font_color"]
        font_path = self._get_font_path()
        font = ImageFont.truetype(font_path, int(self.content_height * 0.9))
        # size
        width = self.tile_config["width"]
        left = width - (width - right) // 2
        top = self.tile_config["height"] // 2
        # text
        text = Api(self.tile_config).get_text()
        print(f"{self.tile_slug}: tile response {text}")
        draw.text((left, top), text, fill=font_color, anchor="mm", font=font)

    def _get_font_path(self):
        """build path to font"""
        font_conf = self.tile_config.get("font")
        if not font_conf:
            return self.FONT_DEFAULT

        if font_conf.startswith("liberation"):
            return path.join("/usr/share/fonts/truetype", font_conf)

        if font_conf.startswith("ttf-bitstream-vera"):
            return path.join("/usr/share/fonts/truetype", font_conf)

        if font_conf.startswith("fonts/"):
            return path.join("/data", font_conf)

        return self.FONT_DEFAULT

    def save_tile(self):
        """save tile to disk"""
        file_path = path.join(self.TILE_BASE, self.tile_slug + ".png")
        self.img.save(file_path)


def create_all_tiles():
    """create all tiles needed"""
    config = TilefyRedis().get_message("config")
    if not config:
        print("no tiles defined in tiles.yml")
        return

    for tile_slug, tile_config in config["tiles"].items():
        create_single_tile(tile_slug, tile_config)


def create_single_tile(tile_slug, tile_config):
    """create a single tile"""
    key = f"lock:{tile_slug}"
    locked = TilefyRedis().get_message(key)
    if locked:
        print(f"{tile_slug}: skip rebuild within 60secs")
        return

    TileImage(tile_slug, tile_config).build_tile()
    message = {"recreate": int(datetime.now().strftime("%s"))}
    TilefyRedis().set_message(key, message, expire=60)
