Pokébot
=============
Slack chat-bot that can query Wolfram Alpha, Bing, and will also respond to queries on over 700 Pokemon.

The bot will detect any mention of a Pokémon (e.g. pikachu) and respond with a random fact pertaining to the mentioned Pokémon. If you as the bot a question directly using the @yourbotname callout, it will query wolfram Alpha and formulate a response to seem smart. If Wolfram Alpha does not produce an answer, it will then query the Bing API for results. Both the Pokémon functionality and wolfram alpha functionality may be disabled individually if desired.


Usage
-------
You will need an api_token from Slack and optionally an app id from Wolfram Alpha (Free) and optionally an API key from Bing (Free)
Clone this repo and the python-slackbot dependency. Then set-up a configuration YAML file containing slack_token and wolfram_alpha_appid

  python pokebot/pokebot.py --config my_config.yml


Dependencies
-------
https://github.com/bscan/python-slackbot


Disclaimers
-------
Although my code is free to use and fork, all Pokémon are trademarks of Nintendo, and the Pokédex descriptions are copyrighted by Nintendo and are used under Fair Use policy. Wolfram|Alpha is trademarked by Wolfram Research. Bing is trademarked by Microsoft. Pokébot is not affiliated with or endorsed by Nintendo, Wolfram Research, or Microsoft.
