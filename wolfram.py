from data.wolfram_templates import wolfram_templates
import requests
import xml.etree.ElementTree as ET
import random
import traceback
import re

def answers(client, event, wolfram_appid, bingid):
    # This function can also be used directly as a response function if you want to remove the Pokemon stuff

    message = event.get('text_query', '')

    if not event.get('speaking_to_me') or len(message) < 2:
        # Don't waste API calls on mostly empty strings
        return None

    words = [word.lower() for word in message.split() if len(word) > 1]
    image_triggers = ['giphy', 'gif', 'animate', 'animated', 'image', 'picture', 'meme', 'graph', 'chart']
    is_image = len(set(words).intersection(image_triggers)) > 0

    try:
        assert wolfram_appid and not is_image
        # TODO: Enable wolfram images for graphs
        return _wolfram_api(message, wolfram_appid)
    except Exception:
        try:
            assert bingid
            return _bing_api(message, bingid, is_image)
        except Exception:
            traceback.print_exc()
            return random.choice(wolfram_templates['fail'])


def _bing_api(message, bingid, is_image):
    print u"Hitting Bing API for: " + message
    api_loc = 'Image' if is_image else 'Web'
    url = 'https://api.datamarket.azure.com/Bing/Search/v1/' + api_loc
    auth = ('', bingid)
    message = message.replace("'", "''")  # Escape single quotes
    params = {'Query': u"'{0}'".format(message), '$format': 'json', '$top': 1, 'Adult': "'Strict'"}
    response = requests.get(url, auth=auth, params=params)
    #print response.content
    response = response.json()

    if is_image:
        quote = response['d']['results'][0]['MediaUrl']
        # If we get a Giphy, ensure we are using the animated one, not the static ones
        quote = re.sub(r'(giphy\.com\/.*)\/.+_s\.(?:jpe?g|gif)', r'\1/giphy.gif', quote)
    else:
        # Removing the protocol ensures the link doesn't expand in the messages
        link = response['d']['results'][0]['Url'].replace('https://', '').replace('http://', '')
        quote = response['d']['results'][0]['Description'] + u" " + link
    assert len(quote) > 1
    return quote


def _wolfram_api(message, appid):
    print u"Hitting Wolfram|Alpha for: " + message
    params = {'appid': appid, 'input': message, 'format': 'plaintext'}
    response = requests.get('http://api.wolframalpha.com/v2/query', params=params)
    xml_response = ET.fromstring(response.content)
    interpretation = xml_response.findall('pod')[0].find('subpod').find('plaintext').text
    answer = xml_response.findall('pod')[1].find('subpod').find('plaintext').text
    quote = _wolfram_format_quote(interpretation, answer)
    return quote


def _wolfram_format_quote(interpretation, answer):
    # Try to get more conversational version of the input interpretation
    # Example input is "Canada | population"

    # Make sure we got a valid answer, or else we should just try something else
    assert answer
    assert answer != '(data not available)'

    answer = _wolfram_decode(answer)
    interpretation = _wolfram_decode(interpretation)

    parts = interpretation.split(' | ')
    if len(parts) == 0:
        return interpretation + ":" + answer
    elif len(parts) == 1:
        template = random.choice(wolfram_templates['single'])
        return template.format(input=interpretation, answer=answer)
    elif len(parts) == 2:
        template = random.choice(wolfram_templates['double'])
        return template.format(i1=parts[0], i2=parts[1], answer=answer)
    elif len(parts) == 3:
        template = random.choice(wolfram_templates['triple'])
        return template.format(i1=parts[0], i2=parts[1], i3=parts[2], answer=answer)
    else:
        template = random.choice(wolfram_templates['many'])
        return template.format(input=interpretation, answer=answer)


def _wolfram_decode(text):
    # Wolfram Alpha uses unicode private use characters. I can't find a reference, but I've seen them in results.
    text = text.replace(u'\uf7d9', '=')
    return text
