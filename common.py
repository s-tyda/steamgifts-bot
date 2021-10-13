from pyfiglet import figlet_format
from threading import Lock
from typing import Any
from rich import print


def log(string, color, font="slant", figlet=False):
    if not figlet:
        print(f'[{color}]{string}[/{color}]')
    else:
        print(f'[{color}]{figlet_format(string, font=font)}[/{color}]')


class Singleton(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
