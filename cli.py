import configparser
import questionary
import json
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError
from main import SteamGifts
from common import log, Singleton
from typing import Dict, Any
from functools import cached_property


class PointValidator(Validator):
    def validate(self, doc: Document) -> bool:
        value = doc.text
        try:
            value = int(value)
        except Exception:
            raise ValidationError(
                message="Value should be a number",
                cursor_position=len(doc.text),
            )

        if value <= 0:
            raise ValidationError(
                message="Value should be greater than 0",
                cursor_position=len(doc.text),
            )
        return True


class ConfigReader(metaclass=Singleton):
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read("config/config.ini")

    def _save_config(self) -> None:
        with open("config/config.ini", "w") as configfile:
            self.config.write(configfile)

    def _ask_for_cookie(self) -> str:
        cookie = questionary.text(
            "Enter PHPSESSID cookie (Only needed to provide once):"
        ).ask()
        self.config["DEFAULT"]["cookie"] = cookie
        self._save_config()
        return cookie

    def _ask_for_pinned(self) -> bool:
        pinned_games = questionary.confirm(
            "'Should bot enter pinned games?'"
        ).ask()
        self.config["DEFAULT"]["enter_pinned_games"] = str(pinned_games)
        self._save_config()
        return pinned_games

    def _ask_for_min_points(self) -> int:
        min_points = questionary.text(
            message="Enter minimum points to start working (bot will try "
            "to enter giveaways until minimum value is reached):",
            validate=PointValidator,
        ).ask()
        self.config["DEFAULT"]["min_points"] = min_points
        self._save_config()
        return int(min_points)

    @cached_property
    def data(self) -> Dict[str, Any]:
        with open("config/config.json") as json_data_file:
            data = json.load(json_data_file)

        if not self.config["DEFAULT"].get("cookie"):
            data["cookie"] = self._ask_for_cookie()
        else:
            data["cookie"] = self.config["DEFAULT"].get("cookie")

        if not self.config["DEFAULT"].get("enter_pinned_games"):
            data["enter_pinned_games"] = self._ask_for_pinned()
        else:
            data["enter_pinned_games"] = self.config["DEFAULT"].getboolean(
                "enter_pinned_games"
            )

        if not self.config["DEFAULT"].get("min_points"):
            data["min_points"] = self._ask_for_min_points()
        else:
            data["min_points"] = self.config["DEFAULT"].getint("min_points")
        return data


def run() -> None:
    log("SteamGifts Bot", color="blue", figlet=True)
    log("Welcome to SteamGifts Bot!", color="green")
    log("Created by: github.com/s-tyda", color="white")

    config = ConfigReader()
    s = SteamGifts(**config.data)
    s.start()


if __name__ == "__main__":
    run()
