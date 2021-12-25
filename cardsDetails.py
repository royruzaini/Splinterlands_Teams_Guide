import json
import ssl
import urllib.request
import certifi

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

with open('cardsDetails.json') as f:
    card_id = json.load(f)
    cards_legends_summoners = [x['id'] for x in card_id if x['type'] == 'Summoner' and x['rarity'] == 4]
f.close

with open("legendarySummonersCards.json", "w") as f:
    f.write(json.dumps(cards_legends_summoners))
    print("legendarySummonersCards.json file was updated!")
f.close
