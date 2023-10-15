import logging

import requests

FAKE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept-Encoding': '*',
    'Connection': 'keep-alive'
}


class RiotAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def execute_request(url):
        status_code = 0

        while status_code != 200:
            response = requests.get(url, headers=FAKE_HEADERS)

            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f'Error executing request: {response.status_code}: {response.text}: {url}')
                status_code = response.status_code

    def get_active_game_participants(self):
        return self.execute_request(
            f'https://127.0.0.1:2999/liveclientdata/playerlist')

    def get_summoner(self, summoner_name):
        return self.execute_request(
            f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={self.api_key}')

    def get_summoner_by_id(self, summoner_id):
        return self.execute_request(
            f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={self.api_key}')

    def get_summoner_stats(self, summoner_id):
        return self.execute_request(
            f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={self.api_key}')

    def get_match_data(self, match_id):
        return self.execute_request(
            f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}')

    def get_latest_matches_id(self, summoner_puuid, count):
        return self.execute_request(
            f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?type=ranked&queue=420&count={count}&api_key={self.api_key}')


