![Tilefy](assets/tilefy-banner.jpg?raw=true "Tilefy Banner")  

<center><h1>Create beautiful tiles for your project</h1></center>

## Table of contents
- [Core functionality](#core-functionality)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Configuration](#configuration)
- [API requests](#api-requests)
- [Plugins](#plugins)
- [Donate](#donate)

## Core functionality
- Dynamically create and recreate PNG tiles
- Showcase any project stats accessible over a public API
- Customize to your liking with your branding and color scheme
- Embed your tiles anywhere you can embed a image
- Self Hosted with Docker

## Screenshots
![home screenshot](assets/screenshot.png?raw=true "Tilefy Home Page")  

## Installation
Take a look at the example `docker-compose.yml` file provided. Tilefy depends on two containers:

### Tilefy
Main Python application to create and serve your tiles, built with Flask.
- Serves the interface on port `8000`
- Needs a volume at **/data** to store your tiles, custom fonts and logos and your **tiles.yml** config file.
- Set your Redis connection with the environment variables `REDIS_HOST` and `REDIS_PORT`.
- Set the environment variable `TILEFY_HOST` to your full url from where you are hosting this application. Needed to build links and templates to embed your tiles. Don't add a trailing `/`.
- Set your timezone with the `TZ` environment variable to configure the scheduler, defaults to *UTC*.

### Redis JSON
Functions as a cache and holds the scheduler data storage and history.
- Needs a volume at **/data** to store your configurations permanently.

## Configuration
Create a yml config file where you have mounted your `/data/tiles.yml` folder. Take a look at the provided `tiles.example.yml` for the basic syntax. *tiles* is the top level key, list your tiles below. The main key of the tile is your slug and will become your url, so use no spaces or special characters. 

### tile_name
Give your tile a unique human readable name.

### background_color, font_color
Hex color code for background and font, make sure to add the *""* to escape the *#* symbol. 

### width, height
Size of the tile in pixels.

### logos
List of logos, get a list of pre installed logos:
```bash
docker exec -it tilefy ls logos
```
Add the pre installed logos by providing the file name. Contribute by adding additional commonly used logos. 

Provide your custom logos by adding them to `/data/logos/`, in PNG file format with transparent background. Add your custom logos by providing a relative path like `logos/file-name.png`.

### font: optional
Font defaults to *Vera.ttf*. Use a pre installed font from the *liberation* or *ttf-bitstream-vera* packages by providing the relative path from the truetype folder.
List available pre installed fonts:
```bash
docker exec -it tilefy ls /usr/share/fonts/truetype/liberation
docker exec -it tilefy ls /usr/share/fonts/truetype/ttf-bitstream-vera
```

Provide your custom font by adding them to `/data/fonts`, in TTF format only and add them with their relative path like `fonts/font-name.ttf`.

### humanize: optional
Defaults to `true` for all numbers. Shorten long numbers in to a more human readable string, like *14502* to *14.5K*.

### recreate: optional
Recreate tiles periodically, provide your custom schedule as a cron tab or use `on_demand` to recreate the tile for every request. Defaults to `0 0 * * *` aka every day at midnight. Be aware of any rate limiting and API quotas you might face with a too frequent schedule. 
Note:
- There is automatically a random jitter for cron tab of 15 secs to avoid parallel requests for a lot of tiles.
- There is a failsafe in place to block recreating tiles faster than every 60 seconds. 

## API requests
Get values from a public API by providing the url and key_map.

### url
JSON API endpoint. If you can, filter and reduce the API response size by requesting only the required fields.

### key_map
Navigate the JSON object to find your desired value. Each item in the list navigates one level deeper, a `string` accesses a key and a `int` accesses an index in an array. 

*Example 1*
```json
{
    "pull_count": 269912,
    "star_count": 11,
}
```
To for example access the *pull_count* key in the top level of the response:
```yml
key_map:
  - pull_count
```

*Example 2*
```json
{
    "results": [
        {
            "status": "success",
            "last_run": "timestamp",
        }
    ]
}
```

To for example access the *status* key in the first dictionary of the results list:
```yml
key_map:
  - results
  - 0
  - status
```

## Plugins
For all values not accessible over a JSON API endpoint, this will need a dedicated solution by for example scraping the website. This is inherently less reliable as websites change more frequently than APIs.

### Chrome extension users
Get the amount of active chrome extension users.
```yml
plugin:
  name: chrome-extension-users
  id: jjnkmicfnfojkkgobdfeieblocadmcie
```

Please contribute and open feature requests to add more.

## Donate
The best donation to **Tilefy** is your time, contribute in any way you can to improve this project.  
Second best way to support the development is to provide for caffeinated beverages:
* [Paypal.me](https://paypal.me/bbilly1) for a one time coffee
* [Paypal Subscription](https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-03770005GR991451KMFGVPMQ) for a monthly coffee
* [ko-fi.com](https://ko-fi.com/bbilly1) for an alternative platform
