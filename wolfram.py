from data.wolfram_templates import wolfram_templates
import requests
import xml.etree.ElementTree as ET
import random
import traceback


def answers(event, wolfram_appid, bingid):
    # This function can also be used directly as a response function if you want to remove the Pokemon stuff

    message = event.get('text_query', '')

    if not event.get('speaking_to_me') or len(message) < 2:
        # Don't waste API calls on mostly empty strings
        return None

    try:
        assert wolfram_appid
        return _wolfram_api(message, wolfram_appid)
    except Exception:
        try:
            assert bingid
            return _bing_api(message, bingid)
        except Exception:
            traceback.print_exc()
            return random.choice(wolfram_templates['fail'])


def _bing_api(message, bingid):
    print u"Hitting Bing API for: " + message
    url = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web'
    auth = ('', bingid)
    message = message.replace("'", '&#39;')
    params = {'Query': u"'{0}'".format(message), '$format': 'json', '$top': 1, 'Adult': "'Strict'"}
    response = requests.get(url, auth=auth, params=params)
    print response.content
    response = response.json()
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


def _wolfram_format_quote(interpretation, answer):
    # Try to get more conversational version of the input interpretation
    # Example input is "Canada | population"

    if not answer:
        answer = random.choice(wolfram_templates['answer_fail'])

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
