# -*- coding: utf-8 -*-

import random
from slackbot import SlackBot
from data.poketext import pokedex, templates, alternative_desc
from argparse import ArgumentParser
import yaml
from functools import partial
from wolfram import answers


def pikachu(client, event, wolfram_appid=None, bingid=None):
    # Note that all messages get sent here, even if they aren't addressing the bot

    text = event.get('text')
    for pnc in [",", ".", "?", "'", '"', '!', ':', '-']:
        text = text.replace(pnc, ' ')
    words = [word.lower().capitalize() for word in text.split() if len(word) > 1]

    _reactions(client, event, words)

    if event.get('speaking_to_me'):
        # You're talking to me, you want real answers
        return answers(client, event, wolfram_appid, bingid)

    pokemon = list(set(words).intersection(pokedex.keys()))

    if len(pokemon) == 0 and len(set(words).intersection([u'Pokemon'])) == 0:
        # You didn't mention a pokemon or the word "pokemon" and you're not speaking to me
        return None

    return _poke_quote(pokemon)


def _reactions(client, event, words):
    swears = set(words).intersection(['Fuck', 'Fuckity', 'Fucks', 'F***', 'Fucking', 'Fucked', 'Fbomb', 'Fbombs'])
    if len(swears) > 0:
        client.api_call("reactions.add", name='fbomb', channel=event['channel'], timestamp=event['ts'])


def _poke_quote(pokemon):
    if len(pokemon) == 0:
        # Been triggered, but the user didn't specify a specific Pokemon. Draw a random one.
        pokemon = [random.choice(pokedex.keys())]
        odds = {"description": 1, "type": 1, "statement": 2}
    else:
        odds = {"description": 100, "type": 10, "statement": 2}

    if len(pokemon) == 1:
        desc = random.choice(alternative_desc.get(pokemon[0], []) + [pokedex[pokemon[0]].get('description')])
        if not desc: odds['description'] = 0
        ptype = pokedex[pokemon[0]].get('firstType')
        if not ptype: odds['type'] = 0
        quote_choice = random.choice(templates[_weighted_choice(odds)])
        quote = quote_choice.format(name=pokemon[0], ptype=ptype.lower(), desc=desc)
    elif len(pokemon) == 2:
        quote = random.choice(templates['double']).format(pokemon[0], pokemon[1])
    else:  # len(pokemon) > 2:
        quote = random.choice(templates['many']).format(u", ".join([p for p in pokemon[:-1]]) + " and " + pokemon[-1])
    return quote


def _weighted_choice(choices):
    # http://stackoverflow.com/questions/3679694/
    total = sum(w for c, w in choices.items())
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices.items():
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
            '-c',
            '--config',
            help='Full path to config file.',
            metavar='path',
            required=True
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    config = yaml.load(file(args.config, 'r'))
    if config.get('serious_business_mode'):
        response = answers
    else:
        response = pikachu

    bot_function = partial(response, wolfram_appid=config.get('wolfram_alpha_appid'), bingid=config.get('bingid'))
    SlackBot(config['slack_token'], bot_function, only_speaking_to_me=False).start()
