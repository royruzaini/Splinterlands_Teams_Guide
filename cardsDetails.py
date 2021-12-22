import json
import ssl
import urllib.request
import certifi
import requests
import os
from dotenv import load_dotenv

with urllib.request.urlopen('https://api.splinterlands.io/cards/get_details', context=ssl.create_default_context(cafile=certifi.where())) as url:
    data = json.loads(url.read().decode())

with open("cardsDetails.json", "w") as outfile:
    outfile.write(json.dumps(data))
    print("cardsDetails.json file was updated!")
outfile.close

with open('cardsDetails.json') as f:
    card_id = json.load(f)
    cards = [x['id'] for x in card_id if x['editions'] == '7' and x['rarity'] == 1 or x['editions'] == '7' and x['rarity'] == 2 or x['editions'] == '4' and x['rarity'] == 1 or x['editions'] == '4' and x['rarity'] == 2]
f.close

with open("basicCards.json", "w") as f:
    f.write(json.dumps(cards))
    print("basicCards.json file was updated!")
f.close

def get_cards(username):
    """ Get user's playable cards.
    """
    base_cards = [135, 136, 137, 138, 139, 140, 141, 145, 146, 147, 148, 149, 150, 151, 152, 156, 157, 158, 159, 160, 161, 162, 163, 167, 168, 169, 170, 171, 172, 173, 174, 178, 179, 180, 181, 182, 183, 184, 185, 189, 190, 191, 192, 193, 194, 195, 196, 224, 353, 354, 355, 356, 357, 358, 359, 360, 361, 367, 368, 369, 370, 371, 372, 373, 374, 375, 381, 382, 383, 384, 385, 386, 387, 388, 389, 395, 396, 397, 398, 399, 400, 401, 402, 403, 409, 410, 411, 412, 413, 414, 415, 416, 417, 423, 424, 425, 426, 427, 428, 429, 437, 438, 439, 440, 441] 
    p_cards = []

    player_cards_data = requests.get(
        'https://api2.splinterlands.com/cards/collection/' + username.lower()
    )
    player_cards = player_cards_data.json()['cards']

    for p_card in player_cards:
        # checks if base cards have been upgraded
        if p_card['card_detail_id'] in base_cards:
            base_cards.remove(p_card['card_detail_id'])

        p_card_data = {}
        p_card_data['id'] = p_card['card_detail_id']
        p_card_data['level'] = p_card['level']
        p_cards.append(p_card_data)

    for base_card in base_cards:
        base_card_data = {}
        base_card_data['id'] = base_card
        base_card_data['level'] = 1
        p_cards.append(base_card_data)

    with open("mycards.json", "w") as outfile:
        outfile.write(json.dumps(p_cards))
    outfile.close

# load .env variables
load_dotenv(override=True)

# gets global user details
USERNAME = os.getenv('USERNAME').lower()
get_cards(USERNAME)
