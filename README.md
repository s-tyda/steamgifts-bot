# steamgifts-bot

Configurable bot for [steamgifts.com](https://www.steamgifts.com/), which automatically enters giveaways.

## Contents

- [How to run](#how-to-run)
- [Config](#config)
- [Run with docker-compose](#run-with-docker-compose)
- [Build docker image yourself](#build-docker-image-yourself)
- [Run from source](#run-from-source)
- [Help](#help)

## Features
- Automatically enters giveaways.
- Undetectable.
- Сonfigurable.
- Sleeps to restock the points.
- Can run 24/7.

## How to run
1. Install with one of the options below.
2. Sign in on [steamgifts.com](https://www.steamgifts.com/) by Steam.
3. Find `PHPSESSID` cookie in your browser.
4. Configure config files.
5. Start the bot.

## Config
1. Configure `config.ini` file.
```ini
[DEFAULT]
cookie = j06gtgcn7o6f83t4nq6974jngs7dmictv4oinkcqrnfnu8gu
enter_pinned_games = yes
min_points = 20
```
- `cookie` is the place for your PHPSESSID cookie.
- `enter_pinned_games` checks if the bot should enter pinned games.
- `min_points` is the minimum points account should have to make the bot enter giveaways.

2. Configure `config.json` file.
```json
{
  "filters": {
    "All": "search?page=%d&dlc=false",
    "Wishlist": "search?page=%d&type=wishlist&dlc=false",
    "Recommended": "search?page=%d&type=recommended&dlc=false",
    "Copies": "search?page=%d&copy_min=2&dlc=false",
    "DLC": "search?page=%d&dlc=true",
    "Group": "search?page=%d&type=group&dlc=false",
    "New": "search?page=%d&type=new&dlc=false"
  },
  "priorities": [
    "Group",
    "Copies",
    "Recommended",
    "Wishlist",
    "All"
  ]
}
```
- `filters` object contains all url filters from the SteamGifts, where the key is name to use in priorities and value is the filter.
- `priorities` object contains filters, in order, which bot should enter.

## Run with docker-compose
1. Download [latest release](https://github.com/s-tyda/steamgifts-bot/releases/latest) or clone the code.
2. Enter project directory.
```bash
cd steamgifts-bot/
```
3. Run docker-compose.
```bash
docker-compose up -d
```
To stop container:
```bash
docker-compose down
```
To see container logs:
```bash
docker-compose logs -f
```
To update official docker image
```bash
docker pull ghcr.io/s-tyda/steamgifts-bot:master
```

## Build docker image yourself
1. Clone repository.
2. Enter project directory.
```bash
cd steamgifts-bot/
```
3. Build image.
```bash
docker build -t steamgifts-bot .
```
4. Run container.
```bash
docker run -d steamgifts-bot
```
To stop container:
```bash
docker stop container-id
```
To see container logs:
```bash
docker logs --follow container-id
```

## Run from source
1. Clone repository.
2. Enter project directory.
```bash
cd steamgifts-bot/
```
3. Install dependencies.
```bash
pip install -r requirements.txt
```
4. Run script.
```bash
python src/cli.py
```

## Help
Please leave your feedback and bugs in `Issues` page.
