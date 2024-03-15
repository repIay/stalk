import json, time
from valclient.client import Client
from player import Player
from game import Game

running = True
seenMatches = []

print('valorant stalker ^_^ @azuroh on disc')

with open('settings.json', 'r') as f:
    data = json.load(f)
    ranBefore = data['ran']
    region = data['region']
    stateInterval = data['stateInterval']
    twitchReqDelay = data['twitchReqDelay']
    skipTeamPlayers = data['skipTeamPlayers']
    skipPartyPlayers = data['skipPartyPlayers']

if (ranBefore == False):
    region = input("Enter your region: ").lower()
    client = Client(region=region)
    client.activate()

    with open('settings.json', 'w') as f:
            data['ran'] = True
            data['region'] = region
            json.dump(data, f, indent=4)
else:
    client = Client(region=region)
    client.activate()

print("waiting for the game")
while (running):
    time.sleep(30)
    try:
        sessionState = client.fetch_presence(client.puuid)['sessionLoopState']
        matchID = client.coregame_fetch_player()['MatchID']

        if (sessionState == "INGAME" and matchID not in seenMatches):
            print('-'*55)
            print("match found")
            seenMatches.append(matchID)
            matchInfo = client.coregame_fetch_match(matchID)
            players = []

            for player in matchInfo['Players']:
                if (client.puuid == player['Subject']):
                    localPlayer = Player(
                        client=client,
                        puuid=player['Subject'].lower(),
                        agentID=player['CharacterID'].lower(),
                        incognito=player['PlayerIdentity']['Incognito'],
                        team=player['TeamID']
                    )
                else:
                    players.append(Player(
                        client=client,
                        puuid=player['Subject'].lower(),
                        agentID=player['CharacterID'].lower(),
                        incognito=player['PlayerIdentity']['Incognito'],
                        team=player['TeamID']
                    ))
            
            currentGame = Game(party=client.fetch_party(), matchID=matchID, players=players, localPlayer=localPlayer)
            print("\nsearching for hidden names\n")
            currentGame.find_hidden_names(players)
            
            print("\nfinding possible streamers\n")
            currentGame.find_streamers(players, twitchReqDelay, skipTeamPlayers, skipPartyPlayers)

    except Exception as e:
        if ("core" not in str(e)) and ("NoneType" not in str(e)):
            print("an error occurred:", e)
