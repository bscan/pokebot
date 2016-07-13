# -*- coding: utf-8 -*-

import random
from slackbot import SlackBot
from data.poketext import pokedex, templates, alternative_desc
from argparse import ArgumentParser
import yaml
from functools import partial
from wolfram import answers
import string
import re
import time

def pikachu(client, event, wolfram_appid=None, bingid=None):
    # Note that all messages get sent here, even if they aren't addressing the bot

    text = event.get('text')
    for pnc in u"“”" + string.punctuation.replace(':', ''): # Remove : so emoji's don't get repeated
        text = text.replace(pnc, ' ')
    words = [word.lower().capitalize() for word in text.split() if len(word) > 1]

    cmd_response = _commands(client, event, words)

    if cmd_response:
        return cmd_response
    elif event.get('speaking_to_me'):
        # You're talking to me, you want real answers
        return answers(client, event, wolfram_appid, bingid)
    else:
        pokemon = list(set(words).intersection(pokedex.keys()))

        if len(pokemon) == 0:
            # You didn't mention and you're not speaking to me
            return None
        else:
            for pokemon_name in pokemon:
                try:
                    results = client.api_call("reactions.add", name=pokemon_name.lower() + '2', channel=event['channel'], timestamp=event['ts'])
                    if not results['ok']:
                        client.api_call("reactions.add", name=pokemon_name.lower(), channel=event['channel'], timestamp=event['ts'])
                except Exception as e:
                        pass
            return None


def _commands(client, event, words):
    # TODO: move all this stuff into the config file

    text = event.get('text')

    if text.lower() == 'standup!':
        members = _get_quasirandom_userlist(client, event)
        response_message = """Hey, <!channel> , it's time for our :slack: Standup! Respond with:
       I am working on OPTI-XXXX and (more details here)
Check out your <https://nanigans.atlassian.net/secure/RapidBoard.jspa?rapidView=11&quickFilter=27|Jira board>!
Today's standup order will be {order}
<@{user}>, you're first!""".format(order=", ".join(members), user=members[0])
        # Links only work via API, not the RTM client
        client.api_call("chat.postMessage", text=response_message, channel=event['channel'], as_user=True)
        return ""

    tickets = re.findall("((?i)OPTI-\d+|OPTR-\d+|PARCH-\d+|AN-\d+)", text)
    if tickets:
        links = [" <https://nanigans.atlassian.net/browse/{ticket}|{ticket}> ".format(ticket=ticket) for ticket in tickets]
        members = _get_quasirandom_userlist(client, event)
        username = event.get('username')

        compliments = ['Great Job {user} on {links}!', '{user}, nice work on {links}!', "{user}'s tickets: {links}.",
                       "Oh yeah, {links}. Challenging stuff.", "Crushing it on {links}.",
                       ":hand: High five {user} on {links}.", ":thumbsup: {user} on {links}."]

        prompts = ["<@{user}>, you're up.", "<@{user}> is next.", "Next up is <@{user}>.", "Ok, <@{user}>'s turn."]
        after = ["({user} is after)", "({user} is on deck)", '({user} can start thinking)']
        final = ["I think that's everybody", "Did I miss anyone?", "Anyone else?"]

        message = random.choice(compliments).format(user=username, links=", ".join(links))

        idx = members.index(username)
        if idx < len(members) - 1:
            next_up = members[idx + 1]
            message += " " + random.choice(prompts).format(user=next_up)

            if idx < len(members) - 2:
                on_deck = members[idx + 2]
                message += " " + random.choice(after).format(user=on_deck)
        else:
            message += " " + random.choice(final)

        # message = "Great Job on " + ", ".join(links) + "!" + "\n" + "Who's up next?"
        print "Sending" + message + " to: " + str(event['channel'])
        client.api_call("chat.postMessage", text=message, channel=event['channel'], as_user=True)
        return ""

    # if text.lower().startswith('interns'): # and event.get('channel') == 'C054GJYFE':
    #     responses = ['Pinging', 'Announcement for', 'I think that was meant for']
    #     return random.choice(responses) + " <@bscannell> and <@magic>"

    return None


def _get_quasirandom_userlist(client, event, excluded_users=['opt-bot', 'internpikachu', 'quip']):
    # Returns a "randomly" sorted list of users in channel that will keep the same order throughout the day

    channel_obj = client.server.channels.find(str(event['channel']))
    members = [client.server.users.find(member).name for member in channel_obj.members]
    members = [x for x in members if x not in excluded_users]

    # Get temporary random number generator based on todays date
    myrandom = random.Random(int(time.strftime("%Y%m%d")))
    myrandom.shuffle(members)

    return members


def _reactions(client, event, words):
    swears = set(words).intersection(['Fuck', 'Fuckity', 'Fucks', 'F***', 'Fucking', 'Fucked', 'Fbomb', 'Fbombs'])
    if len(swears) > 0:
        client.api_call("reactions.add", name='fbomb', channel=event['channel'], timestamp=event['ts'])



# def _poke_quote(pokemon):
#     if len(pokemon) == 0:
#         # Been triggered, but the user didn't specify a specific Pokemon. Draw a random one.
#         pokemon = [random.choice(pokedex.keys())]
#         odds = {"description": 1, "type": 1, "statement": 2}
#     else:
#         odds = {"description": 100, "type": 10, "statement": 2}
#
#     if len(pokemon) == 1:
#         desc = random.choice(alternative_desc.get(pokemon[0], []) + [pokedex[pokemon[0]].get('description')])
#         if not desc: odds['description'] = 0
#         ptype = pokedex[pokemon[0]].get('firstType')
#         if not ptype: odds['type'] = 0
#         quote_choice = random.choice(templates[_weighted_choice(odds)])
#         quote = quote_choice.format(name=pokemon[0], ptype=ptype.lower(), desc=desc)
#     elif len(pokemon) == 2:
#         quote = random.choice(templates['double']).format(pokemon[0], pokemon[1])
#     else:  # len(pokemon) > 2:
#         quote = random.choice(templates['many']).format(u", ".join([p for p in pokemon[:-1]]) + " and " + pokemon[-1])
#     return quote
#
#
# def _weighted_choice(choices):
#     # http://stackoverflow.com/questions/3679694/
#     total = sum(w for c, w in choices.items())
#     r = random.uniform(0, total)
#     upto = 0
#     for c, w in choices.items():
#         if upto + w >= r:
#             return c
#         upto += w
#     assert False, "Shouldn't get here"


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
