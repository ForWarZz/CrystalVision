import json
from sklearn.preprocessing import LabelEncoder


class Encoders:
    position_encoder: LabelEncoder
    champion_name_encoder: LabelEncoder

    def __init__(self, champions_name):
        self.position_encoder = LabelEncoder().fit(['unknown', 'TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY'])
        self.champion_name_encoder = LabelEncoder().fit(champions_name)


def preprocess_champion_name(champion_name):
    return champion_name.replace(' ', '').replace("'", '').lower()


def rank_to_mmr(tier, division):
    if division == 'I':
        division = 1
    elif division == 'II':
        division = 2
    elif division == 'III':
        division = 3
    elif division == 'IV':
        division = 4

    if tier == 'IRON':
        return 0 + (division - 1) * 100
    elif tier == 'BRONZE':
        return 400 + (division - 1) * 100
    elif tier == 'SILVER':
        return 800 + (division - 1) * 100
    elif tier == 'GOLD':
        return 1200 + (division - 1) * 100
    elif tier == 'PLATINUM':
        return 1600 + (division - 1) * 100
    elif tier == 'EMERALD':
        return 1800 + (division - 1) * 100
    elif tier == 'DIAMOND':
        return 2000 + (division - 1) * 100
    elif tier == 'MASTER':
        return 2200 + (division - 1) * 100
    elif tier == 'GRANDMASTER':
        return 2400 + (division - 1) * 100
    elif tier == 'CHALLENGER':
        return 2600 + (division - 1) * 100

    return 0
