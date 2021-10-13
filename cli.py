import configparser
import json
from PyInquirer import (Token, ValidationError, Validator, prompt, style_from_dict)
from prompt_toolkit import document
from main import SteamGifts
from common import log

config = configparser.ConfigParser()
config.read('config.ini')

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Selected: '#0abf5b',
    Token.Pointer: '#673ab7 bold',
})


class PointValidator(Validator):
    def validate(self, doc: document.Document):
        value = doc.text
        try:
            value = int(value)
        except Exception:
            raise ValidationError(message='Value should be greater than 0', cursor_position=len(doc.text))

        if value <= 0:
            raise ValidationError(message='Value should be greater than 0', cursor_position=len(doc.text))
        return True


def ask(question_type, name, message, validate=None, choices=None):
    questions = [
        {
            'type': question_type,
            'name': name,
            'message': message,
            'validate': validate,
        },
    ]
    if choices:
        questions[0].update({
            'choices': choices,
        })
    answers = prompt(questions, style=style)
    return answers


def ask_for_cookie():
    cookie = ask(question_type='input',
                 name='cookie',
                 message='Enter PHPSESSID cookie (Only needed to provide once):')
    config['DEFAULT']['cookie'] = cookie['cookie']

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    return cookie['cookie']


def run():
    log("SteamGifts Bot", color="blue", figlet=True)
    log("Welcome to SteamGifts Bot!", "green")
    log("Created by: github.com/s-tyda", "white")

    if not config['DEFAULT'].get('cookie'):
        cookie = ask_for_cookie()
    else:
        cookie = config['DEFAULT'].get('cookie')

    if not config['DEFAULT'].get('pinned'):
        pinned_games = ask(question_type='confirm',
                           name='pinned',
                           message='Should bot enter pinned games?')['pinned']
        config['DEFAULT']['pinned'] = pinned_games
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        pinned_games = config['DEFAULT'].getboolean('pinned')

    if not config['DEFAULT'].get('min_points'):
        min_points = ask(question_type='input',
                         name='min_points',
                         message='Enter minimum points to start working '
                                 '(bot will try to enter giveaways until minimum value is reached):',
                         validate=PointValidator)['min_points']
        config['DEFAULT']['min_points'] = min_points
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        min_points = config['DEFAULT'].getint('min_points')

    priorities = data["priorities"]
    filters = data["filters"]

    s = SteamGifts(cookie=cookie, priorities=priorities, filters=filters, pinned=pinned_games, min_points=min_points)
    s.start()


if __name__ == '__main__':
    run()
