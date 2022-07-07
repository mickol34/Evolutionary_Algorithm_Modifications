import random


def gaussian_mutation(point):
    max_lim = 100            # constant
    min_lim = -max_lim       # constant
    sigma = 1                # constant
    new_point = []
    for cord in point:
        new_cord = random.gauss(cord, sigma)
        new_cord = min(max_lim, max(new_cord, min_lim))
        new_point.append(new_cord)
    return tuple(new_point)


def uniform_mutation(point):
    max_lim = 100           # constant
    min_lim = -max_lim      # constant
    max_diff = 1            # constant
    new_point = []
    for cord in point:
        new_cord = random.uniform(max_diff, -max_diff)
        new_cord = min(max_lim, max(new_cord, min_lim))
        new_point.append(new_cord)
    return tuple(new_point)
