from collections import defaultdict

import data_processing
from api import RiotAPI

from data_processing import preprocess_champion_name

STAT_KEYS = ['kills', 'deaths', 'assists', 'goldEarned',
             'goldSpent', 'totalMinionsKilled']


class StatsManager:
    riot_api: RiotAPI

    def __init__(self, riot_api, encoders):
        self.riot_api = riot_api
        self.encoders = encoders

    def get_participant_rank_encoded(self, summoner_id):
        summoner_stats_all_queues = self.riot_api.get_summoner_stats(summoner_id)
        summoner_ranked_stats = next(
            (queue for queue in summoner_stats_all_queues if queue['queueType'] == 'RANKED_SOLO_5x5'), None)

        if summoner_ranked_stats is not None:
            return (data_processing.rank_to_mmr(summoner_ranked_stats['tier'], summoner_ranked_stats['rank']),
                    summoner_ranked_stats['leaguePoints'],
                    summoner_ranked_stats['wins'] / (summoner_ranked_stats['wins'] + summoner_ranked_stats['losses']))

        return None

    def get_participant_stats_encoded(self, summoner_id, summoner_puuid, live_champion_name, live_team_position):
        latest_matches_id = self.riot_api.get_latest_matches_id(summoner_puuid, 5)

        average_stats = defaultdict(None)
        champion_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})
        team_position_stats = defaultdict(int)

        total_team_kills = 0
        matches_wins = 0

        for match_id in latest_matches_id:
            match_data = self.riot_api.get_match_data(match_id)

            for participant in match_data['info']['participants']:
                if participant['summonerId'] == summoner_id:
                    has_won = participant['win']

                    matches_wins += has_won
                    total_team_kills = sum(mate['kills'] for mate in match_data['info']['participants'] if
                                           mate['teamId'] == participant['teamId'])

                    for stat_key in STAT_KEYS:
                        if stat_key not in average_stats:
                            average_stats[stat_key] = 0

                        average_stats[stat_key] += participant[stat_key]

                    champion_stats[participant['championName']]['wins' if has_won else 'losses'] += 1
                    team_position_stats[participant['teamPosition']] += 1

        win_rate_avg = matches_wins / len(latest_matches_id)

        if total_team_kills > 0:
            kill_participation = average_stats['kills'] / total_team_kills
        else:
            kill_participation = 0

        live_champion_id_game_count = champion_stats[live_champion_name]['wins'] + champion_stats[live_champion_name][
            'losses']

        if live_champion_id_game_count > 0:
            live_champion_win_rate = champion_stats[live_champion_name]['wins'] / live_champion_id_game_count
        else:
            live_champion_win_rate = 0

        main_champion_name = max(champion_stats, key=lambda key: champion_stats[key]['wins'] + champion_stats[key][
            'losses']) if len(champion_stats) > 0 else 'unknown'

        encoded_live_champion_name = \
            self.encoders.champion_name_encoder.transform([preprocess_champion_name(live_champion_name)])[0]

        is_main_champion = int(main_champion_name == live_champion_name)

        main_team_position = max(team_position_stats, key=team_position_stats.get)
        encoded_live_team_position = self.encoders.position_encoder.transform([live_team_position])[0]

        is_main_position = int(main_team_position == live_team_position)

        for stat_key in STAT_KEYS:
            average_stats[stat_key] /= len(latest_matches_id)

        kda = (average_stats['kills'] + average_stats['assists']) / (average_stats['deaths'] + 1)

        return (win_rate_avg, live_champion_win_rate, encoded_live_champion_name, is_main_champion,
                kill_participation, encoded_live_team_position, is_main_position, kda, average_stats['goldEarned'],
                average_stats['goldSpent'], average_stats['totalMinionsKilled'])
