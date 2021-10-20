import json
from random import randint
from time import sleep
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from common import log
from typing import Dict, List, Optional


class SteamGifts:
    def __init__(self, cookie: Dict[str, str], priorities: List[str], filters: Dict[str, str],
                 pinned: bool, min_points: int) -> None:
        self.cookie = {
            'PHPSESSID': cookie
        }
        self.priorities = priorities
        self.pinned = pinned
        self.min_points = min_points

        self.base = "https://www.steamgifts.com"
        self.session = requests.Session()

        self.filters = filters
        self.waiting_for_points = False

        self._update_info()

    def _requests_retry_session(self, retries: Optional[int] = 5,
                                backoff_factor: Optional[float] = 0.3) -> requests.Session:
        session = self.session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get_soup_from_page(self, url: str) -> BeautifulSoup:
        self._requests_retry_session().get(url)
        r = requests.get(url, cookies=self.cookie)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def _update_info(self):
        soup = self._get_soup_from_page(self.base)

        try:
            self.xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
            self.points = int(soup.find('span', {'class': 'nav__points'}).text)
            self.waiting_for_points = False
        except TypeError:
            log("⛔  Cookie is not valid.", "red")
            sleep(10)
            exit()

    @staticmethod
    def _select_if_entered(tag):
        if tag.name == "div":
            classes = tag.get("class", [])
            return "sidebar__entry-insert" in classes and "is-hidden" in classes

    @staticmethod
    def _select_not_entered_game(tag):
        if tag.name == 'div':
            classes = tag.get('class', [])
            return 'is-faded' not in classes and 'giveaway__row-inner-wrap' in classes

    @property
    def has_available_points(self):
        if self.points == 0 or self.points < self.min_points:
            self.waiting_for_points = True
            return False
        else:
            return True

    def enter_giveaways(self, filter_type, page=1):
        txt = f"⚙️  Filtering with filter {filter_type}"
        log(txt, "yellow")
        n = page
        while True:
            if not self.has_available_points:
                break

            txt = "⚙️  Retrieving games from %d page." % n
            log(txt, "magenta")

            filtered_url = self.filters[filter_type] % n
            paginated_url = f"{self.base}/giveaways/{filtered_url}"

            soup = self._get_soup_from_page(paginated_url)

            game_list = soup.find_all(self._select_not_entered_game)

            if not game_list or not len(game_list):
                log("⛔  Page is empty. Selecting next filter.", "red")
                sleep(2)
                break

            for game in game_list:
                if not self.has_available_points:
                    break

                if len(game.get('class', [])) == 2 and not self.pinned:
                    continue

                game_cost = game.find_all('span', {'class': 'giveaway__heading__thin'})[-1]

                if game_cost:
                    game_cost = game_cost.getText().replace('(', '').replace(')', '').replace('P', '')
                else:
                    continue

                game_name = game.find('a', {'class': 'giveaway__heading__name'}).text

                if self.points - int(game_cost) < 0:
                    txt = f"⛔ Not enough points to enter: {game_name}"
                    log(txt, "red")
                    continue

                elif self.points - int(game_cost) >= 0:
                    game_id = game.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2]
                    is_success = self.enter_giveaway(game_id)
                    if is_success:
                        self.points -= int(game_cost)
                        txt = f"🎉 One more game! Has just entered {game_name}"
                        log(txt, "green")
                        sleep(randint(3, 7))

            n = n+1

    def enter_giveaway(self, game_id):
        payload = {'xsrf_token': self.xsrf_token, 'do': 'entry_insert', 'code': game_id}
        entry = requests.post('https://www.steamgifts.com/ajax.php', data=payload, cookies=self.cookie)
        json_data = json.loads(entry.text)

        if json_data['type'] == 'success':
            return True

    def start(self):
        while True:
            self._update_info()

            if self.points >= self.min_points:
                txt = "🤖 Hoho! I am back! You have %d points. Lets hack." % self.points
                log(txt, "blue")
                for filter_type in self.priorities:
                    self.enter_giveaways(filter_type)
            else:
                self.waiting_for_points = True

            if self.waiting_for_points:
                txt = f"🛋️  Sleeping to get more points. We have {self.points} points, " \
                      f"but we need {self.min_points} to start."
                log(txt, "yellow")
            if not self.waiting_for_points:
                log("🛋️  List of games is ended. Waiting 15 mins to update...", "yellow")

            sleep(900)
