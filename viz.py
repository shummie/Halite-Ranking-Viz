from collections import namedtuple
import json
import plotly
from plotly.graph_objs import Scatter
from trueskill import Rating, rate

class Game:

    def __init__(self, json_object):
        self.id = json_object["gameID"]
        self.h = json_object["mapHeight"]
        self.w = json_object["mapWidth"]
        self.name = json_object["replayName"]
        self.timestamp = json_object["timestamp"]
        self.users = []
        for u in range(len(json_object["users"])):
            self.users.append(GameUserInfo(json_object["users"][u]))


class GameUserInfo:

    def __init__(self, json_object):
        self.error_log = json_object["errorLogName"]
        self.oauth_id = json_object["oauthID"]
        self.rank = json_object["rank"]
        self.sigma = json_object["sigma"]
        self.user_id = json_object["userID"]
        self.user_rank = json_object["userRank"]
        if json_object["username"] == "twg16" or json_object["username"] == "KalraA":
            self.user_name = json_object["username"] + " v" + json_object["versionNumber"]
        else:
            self.user_name = json_object["username"]
        self.version = json_object["versionNumber"]


class Player:

    def __init__(self, name):
        self.name = name
        self.rating_data = []
        self.record_match("2017-02-13 06:00:00", Rating(25, 8.333))

    def record_match(self, timestamp, rating):
        self.rating = rating
        self.rating_data.append(PlayerData(timestamp, len(self.rating_data) + 1, rating.mu, rating.sigma))


PlayerData = namedtuple("PlayerData", "timestamp game_number mu sigma")


def do_game(game):
    # Takes a game and stores the results
    game_rank_list = []
    player_list = []
    rating_groups = []
    # Check if the player exists.
    for user_data in game.users:
        if user_data.user_name not in players:
            players[user_data.user_name] = Player(user_data.user_name)
        rating_groups.append({user_data.user_name: players[user_data.user_name].rating})
        game_rank_list.append(user_data.rank)
        player_list.append(user_data.user_name)
    rated_list = rate(rating_groups, game_rank_list)
    for i in range(len(game.users)):
        players[game.users[i].user_name].record_match(game.timestamp, rated_list[i][game.users[i].user_name])


games = []
# To pull data:
# wget "https://halite.io/api/web/game?previousID=2331401&limit=100000" -O games.json --no-check-certificate
# replace previousID value with the last game you DO have. it will stop AT that game and NOT pull it.
directory = "C:/Users/Shummie/Documents/GitHub/Halite-Ranking-Viz/"
games.extend(json.load(open(directory + "data/games-2331402-2359106.json")))
games.extend(json.load(open(directory + "data/games-2359107-2362974.json")))
games.extend(json.load(open(directory + "data/games-2362975-2374581.json")))
games.extend(json.load(open(directory + "data/games-2374582-2384577.json")))
games.extend(json.load(open(directory + "data/games-2384578-2399386.json")))

gamelist = []
for g in games:
    gamelist.append(Game(g))

# Just in case gamelist isn't sorted
gamelist.sort(key=lambda x: x.id)

players = {}

game_count = 0
for g in gamelist:
    game_count += 1
    if game_count % 1000 == 0:
        print(game_count)
    do_game(g)

player_name = "shummie"
mu_data = []
for r_data in players[player_name].rating_data:
    mu_data.append(r_data.mu)

trace0 = Scatter(x=list(range(len(mu_data))), y=mu_data, mode="lines", name="lines")
plotly.offline.plot([trace0], filename="line.html")
