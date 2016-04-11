from data.wolfram_templates import wolfram_templates
import requests
import xml.etree.ElementTree as ET
import random


def wolfram(event, wolfram_appid):
    # This function can also be used directly as a response function if you want to remove the Pokemon stuff

    message = event.get('text_query', '')

    if not event.get('speaking_to_me') or len(message) < 2:
        # Don't waste API calls on mostly empty strings
        return None
    if not wolfram_appid:
        return "Need to provide a Wolfram|Alpha app_id"

    try:
        print u"Hitting Wolfram|Alpha for: " + message
        params = {'appid': wolfram_appid, 'input': message, 'format': 'plaintext'}
        response = requests.get('http://api.wolframalpha.com/v2/query', params=params)
        xml_response = ET.fromstring(response.content)
        interpretation = xml_response.findall('pod')[0].find('subpod').find('plaintext').text
        answer = xml_response.findall('pod')[1].find('subpod').find('plaintext').text
        quote = _wolfram_format_quote(interpretation, answer)
    except Exception:
        # TODO: Enumerate exception types and provide better messaging
        quote = random.choice(wolfram_templates['fail'])
    return quote


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
