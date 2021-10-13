### About
The bot is specially designed for [SteamGifts.com](https://www.steamgifts.com/)

### Features
- Automatically enters giveaways.
- Undetectable.
- Сonfigurable.
- Sleeps to restock the points.
- Can run 24/7.

### How to run
1. Download the latest version: https://github.com/s-tyda/steamgifts-bot/releases
2. Sign in on [SteamGifts.com](https://www.steamgifts.com/) by Steam.
3. Find `PHPSESSID` cookie in your browser.
4. Start the bot and follow instructions.

### Run from source
```bash
pip install -r requirements.txt
python src/cli.py
```

### Pull docker image
```bash
docker pull ghcr.io/s-tyda/steamgifts-bot:master
docker run ghcr.io/s-tyda/steamgifts-bot:master
```

### Or build image yourself
```bash
docker build -t steamgifts-bot .
docker run -d steamgifts-bot
```

### See docker logs
```bash
docker logs --follow container-id
```

### Help
Please leave your feedback and bugs in `Issues` page.
