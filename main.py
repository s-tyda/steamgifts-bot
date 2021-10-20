from __future__ import annotations

import json
from functools import cached_property
from random import randint
from time import sleep
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from common import log


class Page:
    def __init__(self, sg: SteamGifts, filter_type: str, page: int) -> None:
        self.sg = sg
        self.page = page
        filtered_url = sg.filters[filter_type] % page
        paginated_url = f"{sg.base}/giveaways/{filtered_url}"
        soup = sg.get_soup_from_page(paginated_url)
        self.games = [
            Game(sg, tag)
            for tag in soup.find_all(self._select_not_entered_game)
        ]

    @staticmethod
    def _select_if_entered(tag: Tag) -> bool:
        if tag.name == "div":
            classes = tag.get("class", [])
            return (
                "sidebar__entry-insert" in classes and "is-hidden" in classes
            )

    @staticmethod
    def _select_not_entered_game(tag: Tag) -> bool:
        if tag.name == "div":
            classes = tag.get("class", [])
            return (
                "is-faded" not in classes
                and "giveaway__row-inner-wrap" in classes
            )

    @property
    def is_empty(self) -> bool:
        return not self.games or not len(self.games)

    def enter_all_games(self) -> None:
        for game in self.games:
            if not self.sg.has_available_points:
                break

            if game.is_pinned and not self.sg.enter_pinned_games:
                continue

            if self.sg.points - game.cost < 0:
                txt = f"⛔  Not enough points to enter: {game.name}"
                log(txt, "red")
            else:
                is_success = game.enter()
                if is_success:
                    self.sg.points -= game.cost
                    txt = f"🎉  One more game! Has just entered {game.name}"
                    log(txt, "green")

            sleep(randint(3, 7))


class Game:
    def __init__(self, sg: SteamGifts, tag: Tag) -> None:
        self.sg = sg
        self.tag = tag

    @cached_property
    def is_pinned(self) -> bool:
        return len(self.tag.get("class", [])) == 2

    @cached_property
    def cost(self) -> int:
        game_cost = self.tag.find_all(
            "span", {"class": "giveaway__heading__thin"}
        )[-1]
        game_cost = (
            game_cost.getText()
            .replace("(", "")
            .replace(")", "")
            .replace("P", "")
        )
        return int(game_cost)

    @cached_property
    def name(self) -> str:
        return self.tag.find("a", {"class": "giveaway__heading__name"}).text

    @cached_property
    def id(self) -> str:
        return self.tag.find("a", {"class": "giveaway__heading__name"})[
            "href"
        ].split("/")[2]

    def enter(self) -> bool:
        payload = {
            "xsrf_token": self.sg.xsrf_token,
            "do": "entry_insert",
            "code": self.id,
        }

        response = requests.post(
            "https://www.steamgifts.com/ajax.php",
            data=payload,
            cookies=self.sg.cookie,
        )

        json_data = json.loads(response.text)

        if json_data["type"] == "success":
            return True
        else:
            return False


class SteamGifts:
    def __init__(
        self,
        cookie: Dict[str, str],
        priorities: List[str],
        filters: Dict[str, str],
        enter_pinned_games: bool,
        min_points: int,
    ) -> None:
        self.cookie = {"PHPSESSID": cookie}
        self.priorities = priorities
        self.enter_pinned_games = enter_pinned_games
        self.min_points = min_points

        self.base = "https://www.steamgifts.com"
        self.session = requests.Session()

        self.filters = filters
        self.waiting_for_points = False

        self._update_info()

    def _requests_retry_session(
        self, retries: Optional[int] = 5, backoff_factor: Optional[float] = 0.3
    ) -> requests.Session:
        session = self.session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_soup_from_page(self, url: str) -> BeautifulSoup:
        self._requests_retry_session().get(url)
        r = requests.get(url, cookies=self.cookie)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def _update_info(self) -> None:
        soup = self.get_soup_from_page(self.base)

        try:
            self.xsrf_token = soup.find("input", {"name": "xsrf_token"})[
                "value"
            ]
            self.points = int(soup.find("span", {"class": "nav__points"}).text)
        except TypeError:
            log("⛔  Cookie is not valid.", "red")
            exit()

    @property
    def has_available_points(self) -> bool:
        if self.points == 0 or self.points < self.min_points:
            return False
        else:
            return True

    def enter_giveaways(self, filter_type: str, start_page: int = 1) -> None:
        txt = f"⚙  Filtering with filter {filter_type}"
        log(txt, "yellow")

        page_number = start_page

        while self.has_available_points:
            txt = f"⚙  Retrieving non-entered games from {page_number} page."
            log(txt, "magenta")

            page = Page(self, filter_type, page_number)

            if page.is_empty:
                log("⛔  Page is empty. Selecting next filter.", "red")
                sleep(2)
                break

            page.enter_all_games()

            page_number = page_number + 1

    def start(self) -> None:
        while True:
            self._update_info()

            if self.has_available_points:
                txt = (
                    "🤖  Hoho! I am back! You have %d points. Lets hack."
                    % self.points
                )
                log(txt, "blue")
                for filter_type in self.priorities:
                    self.enter_giveaways(filter_type)
                    if not self.has_available_points:
                        break

            if self.has_available_points:
                txt = (
                    f"🛋️  Sleeping to get more points. "
                    f"We have {self.points} points, "
                    f"but we need {self.min_points} to start."
                )
            else:
                txt = (
                    "🛋️  List of games is ended. Waiting 15 mins to update..."
                )

            log(txt, "yellow")

            sleep(900)
