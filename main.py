import time

import json
import numpy as np

import tensorflow as tf

from data_processing import Encoders
from stats import StatsManager
from api import RiotAPI


def get_champion_name_by_id(champion_id):
    for champion in champion_data.values():
        if champion['key'] == str(champion_id):
            return champion['name'].lower()


if __name__ == '__main__':
    # Load the model
    model = tf.keras.models.load_model('./model.h5')

    # Sleep to avoid rate limit
    # time.sleep(2 * 60)

    # Load champion.json
    with open('champion.json', encoding='utf-8') as file:
        champion_data = json.load(file)['data']

    champions_name = [champion_name.lower() for champion_name in champion_data.keys()]
    champions_name.append('unknown')

    # Init encoders
    encoders = Encoders(champions_name)

    # Init Riot API
    riot_api = RiotAPI('API_KEY')
    stats_manager = StatsManager(riot_api, encoders)

    # # Get summoner name
    # summoner_name = input("Enter summoner name: ")
    #
    # # Get summoner ID
    # summoner_data = riot_api.get_summoner(summoner_name)
    # summoner_id = summoner_data['id']

    # Get game to predict from summoner id
    # active_game_participants = riot_api.get_active_game_participants()

    # Get participants data (champion, position...)
    participants_data = list()
    #
    # print('Getting participants data...')
    # for participant in active_game_participants:
    #     summoner_name = participant['summonerName']
    #     summoner_id = riot_api.get_summoner(summoner_name)['id']
    #     champion_name = participant['championName']
    #     team_position = participant['position']
    #
    #     participant_rank = stats_manager.get_participant_rank_encoded(summoner_id)
    #     participant_stats = stats_manager.get_participant_stats_encoded(summoner_id, champion_name, team_position)
    #
    #     participant_data = list()
    #     participant_data.extend(participant_rank)
    #     participant_data.extend(participant_stats)
    #
    #     participants_data.append(participants_data)

    for participant in riot_api.get_match_data('EUW1_6577445057')['info']['participants']:
        summoner_puuid = participant['puuid']
        summoner_id = participant['summonerId']
        champion_name = get_champion_name_by_id(participant['championId'])
        team_position = participant['teamPosition']

        participant_rank = stats_manager.get_participant_rank_encoded(summoner_id)
        participant_stats = stats_manager.get_participant_stats_encoded(summoner_id, summoner_puuid, champion_name, team_position)

        participant_data = list()
        participant_data.extend(participant_rank)
        participant_data.extend(participant_stats)

        participants_data.append([x / 255.0 for x in participant_data])

    # Predict the winner
    print('Predicting winner...')

    model_input = list()
    for participant_data in participants_data:
        model_input.extend(participant_data)

    model_input = np.array(model_input).astype(np.float32)
    model_input = tf.convert_to_tensor([model_input])
    prediction = model.predict(model_input)
    winning_prediction = prediction[0][0]

    if winning_prediction > 0.5:
        print(f"L'équipe bleue possède {round(winning_prediction * 100, 2)}% de chance de gagner la partie.")
    else:
        print(f"L'équipe rouge possède {round((1 - winning_prediction) * 100, 2)}% de chance de gagner la partie.")

