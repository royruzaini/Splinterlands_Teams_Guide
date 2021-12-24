from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, View 
import json
import pandas as pd
import requests

# Create your views here.
def home(request):
    return render(request, "home.html")

def monster_color(id):
    with open('cardsDetails.json') as f:
        card_id = json.load(f)
    color = [x['color'] for x in card_id if x['id'] == id]
    color = ''.join(color)
    return color

def card_name(id):
    with open('cardsDetails.json') as f:
        card_id = json.load(f)
    name = [x['name'] for x in card_id if x['id'] == id]
    name = ''.join(name)
    return name

def splinter(color):
    if color == 'Blue':
        return 'Water'
    elif color == 'Red':
        return 'Fire'
    elif color == 'Green':
        return 'Earth'
    elif color == 'Gold':
        return 'Dragon'
    elif color == 'Black':
        return 'Death'
    elif color == 'White':
        return 'Life'
    elif color == 'Gray':
        return 'Neutral'
    else :
        return None

with open("mycards.json") as file:
    mycards = json.load(file)
file.close

with open('collection.json') as f:
    BATTLEBASE = json.load(f)
f.close

class Api(TemplateView):
    # Create your views here.
    def get_cards(request):
        """ Get user's playable cards.
        """
        username = request.GET.get("username")
      
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

        data = "mycards.json successfully created!"
        return HttpResponse(data)

    def getteamwhite(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Life':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Life':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:

            for battle in deck:

                most_win_deck = {}

                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))

                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Life Team Available"
            return HttpResponse(data)

    def getteamblack(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")
     
        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Death':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Death':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:
    
            for battle in deck:

                most_win_deck = {}

                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))
        
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Death Team Available"
            return HttpResponse(data)

    def getteamblue(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")
      
        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Water':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Water':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:
    
            for battle in deck:

                most_win_deck = {}
 
                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))
        
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Water Team Available"
            return HttpResponse(data)

    def getteamred(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")
      
        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Fire':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Fire':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:
    
            for battle in deck:

                most_win_deck = {}
 
                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))
        
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Fire Team Available"
            return HttpResponse(data)

    def getteamgreen(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Earth':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Earth':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:
    
            for battle in deck:

                most_win_deck = {}
 
                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))
        
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Earth Team Available"
            return HttpResponse(data)

    def getteamgold(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")
      
        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Dragon':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Dragon':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, BATTLEBASE))

        possible_decks = []

        for battle in db_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        max = 0
        for battle in possible_decks:
            if battle['amount'] > max :
                max = battle['amount']
        def most_win(battle):
            if battle['amount'] == max:
                return True
            else:
                return False
        deck = list(filter(most_win, possible_decks))

        if len(possible_decks) != 0:
  
            for battle in deck:

                most_win_deck = {}

                most_win_deck['card'] = []         
                most_win_deck['card'].append('summoner')
                most_win_deck['id'] = []
                most_win_deck['id'].append(battle['summoner_id'])
                most_win_deck['name'] = []
                most_win_deck['name'].append(card_name(int(battle['summoner_id'])))
                most_win_deck['splinter'] = []
                most_win_deck['splinter'].append(splinter(monster_color(int(battle['summoner_id']))))
        
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "" :
                        most_win_deck['card'].append('monster_'+str(x+1))
                        most_win_deck['id'].append(battle['monster_'+str(x+1)+'_id'])
                        most_win_deck['name'].append(card_name(int(battle['monster_'+str(x+1)+'_id'])))
                        most_win_deck['splinter'].append(splinter(monster_color(int(battle['monster_'+str(x+1)+'_id']))))

            df = pd.DataFrame(most_win_deck)
            data = df.to_html(classes='table table-bordered')
            return HttpResponse(data)
        else:
            data = "No Dragon Team Available"
            return HttpResponse(data)

    def getteamwhitewin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Life':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Life':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)

    def getteamblackwin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Death':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Death':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)

    def getteambluewin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Water':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Water':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)

    def getteamredwin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Fire':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Fire':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)

    def getteamgreenwin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Earth':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Earth':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)

    def getteamgoldwin(request):

        mana = request.GET.get("mana")
        rule1 = request.GET.get("rule1")
        rule2 = request.GET.get("rule2")

        def filter_deck_all(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana):
                    return True
                else:
                    return False
        all_decks = list(filter(filter_deck_all, BATTLEBASE))

        possible_decks = []

        for battle in all_decks:
            viable = False

            player_summoner = [card for card in mycards if card['id'] == battle['summoner_id']]
            # checks if player has card with battle summoner card_detail_id
            if len(player_summoner) == 0:
                viable = False
            else:
                for x in range(0, 6):
                    if battle['monster_'+str(x+1)+'_id'] != "":
                        player_monster = [card for card in mycards if card['id'] == battle['monster_'+str(x+1)+'_id']]
                        # checks if player has card with battle monster card_detail_id
                        if len(player_monster) > 0:
                            viable = True
                            # assigns player card to first instance returned from cards
                            # player_monster = player_monster[0]
                            # checks if levels match
                            # if battle_monster['level'] == player_monster['level']:
                            #     viable = True
                            # else:
                            #     viable = False
                            #     break
                        else:
                            viable = False
                            break
            if viable:          
                possible_decks.append(battle)

        def filter_deck(battle):
            if rule2 == "None":
                if battle['ruleset'] == rule1 and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Dragon':
                    return True
                else:
                    return False
            else:
                rule = rule1+"|"+rule2
                if battle['ruleset'] == rule and battle['mana_cap'] == int(mana) and battle['summoner_splinter'] == 'Dragon':
                    return True
                else:
                    return False
        db_decks = list(filter(filter_deck, possible_decks))

        max = 0
        for battle in db_decks:
            if battle['amount'] > max :
                max = battle['amount']

        if len(possible_decks) != 0:
            Team = {}
            Team['Possible Team'] = len(possible_decks)
            Team['This Team win'] = max
            Team['Win %'] = round((max / len(possible_decks) * 100),2)

            dg = pd.DataFrame(Team, index=[0])
            win_ratio = dg.to_html(classes='table table-bordered')
            return HttpResponse(win_ratio)