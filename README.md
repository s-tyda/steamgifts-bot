### About
The bot is specially designed for [SteamGifts.com](https://www.steamgifts.com/)

### Features
- Automatically enters giveaways.
- Undetectable.
- Сonfigurable.
- Sleeps to restock the points.
- Can run 24/7.

### How to run
1. Download docker image or clone the code.
2. Sign in on [SteamGifts.com](https://www.steamgifts.com/) by Steam.
3. Find `PHPSESSID` cookie in your browser.
4. Configure config files.
5. Start the bot.

### Config
1. Configure **config.ini** file.
```ini
[DEFAULT]
cookie = 
pinned = yes
min_points = 20
```
- **cookie** is the place for your PHPSESSID cookie.
- **pinned** checks if the bot should enter pinned games.
- **min_points** is the minimum points account should have to make the bot enter giveaways.

2. Configure **config.json** file.
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
- **filters** object contains all url filters from the SteamGifts, where the key is name to use in priorities and value is the filter.
- **priorities** object contains filters, in order, which bot should enter.

### Run from source
```bash
pip install -r requirements.txt
python src/cli.py
```

### Pull docker image (actually using default config.json only)
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
