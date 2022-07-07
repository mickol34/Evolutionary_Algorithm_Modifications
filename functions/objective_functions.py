from math import exp, sqrt, cos, pi, e


def ackley(datapoint):
    x, y = datapoint
    return -20.0 * exp(-0.2 * sqrt(0.5 * (x ** 2 + y ** 2))) - exp(0.5 * (cos(2 * pi * x) + cos(2 * pi * y))) + e + 20
