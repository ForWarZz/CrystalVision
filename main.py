import json
import numpy as np

import tensorflow as tf

from utils.data_processing import Encoders
from utils.stats import StatsManager
from utils.api import RiotAPI


if __name__ == '__main__':
    # Load the model
    model = tf.keras.models.load_model('./model.h5')

    # Load champion.json
    with open('utils/champion.json', encoding='utf-8') as file:
        champion_data = json.load(file)['data']

    champions_name = [champion_name.lower() for champion_name in champion_data.keys()]
    champions_name.append('unknown')

    # Init encoders
    encoders = Encoders(champions_name)

    # Init Riot API
    riot_api = RiotAPI('API_KEY')
    stats_manager = StatsManager(riot_api, encoders)

    # Get game to predict from summoner id
    active_game_participants = riot_api.get_active_game_participants()

    # Get participants data (champion, position...)
    participants_data = list()

    print('Getting participants data...')
    for participant in active_game_participants:
        summoner_name = participant['summonerName']
        summoner_data = riot_api.get_summoner(summoner_name)
        summoner_id = summoner_data['id']
        summoner_puuid = summoner_data['puuid']
        champion_name = participant['championName']
        team_position = participant['position']

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

