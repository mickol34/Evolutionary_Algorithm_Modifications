import random
from utils.algorithms import max_value_points_from_dictionary
from utils.algorithms import min_value_points_from_dictionary


def tournament_selection_max(population):
    s = 5           # constant
    tournament = {}
    for i in range(s):
        random_key = random.choice(list(population.keys()))
        tournament[random_key] = population[random_key]
    return max_value_points_from_dictionary(tournament, 1)[0]


def tournament_selection_min(population):
    s = 5           # constant
    tournament = {}
    for i in range(s):
        random_key = random.choice(list(population.keys()))
        tournament[random_key] = population[random_key]
    return min_value_points_from_dictionary(tournament, 1)[0]
