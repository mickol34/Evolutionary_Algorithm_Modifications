# import heapq
import math
import time
import os

# from utils.DataVisualiser import DataVisualiser
from contextlib import nullcontext
from typing import Callable

import cec2017.functions
import numpy
from cec2017 import functions

from utils.DataVisualiser import DataVisualiser
from utils.algorithms import min_value_points_from_dictionary, get_t_max
from functions import get_function


# UTILS
def save_to_data(q_name, pop_f_name, dims, b_cords, b_value):
    dirname = os.path.dirname(__file__)
    filename = f"data/{q_name}_{pop_f_name}_{dims}.txt"  # DLA 5,5 DODAĆ CONST ZAMIAST POP_F_NAME
    path_to_file = os.path.join(dirname, filename)
    with open(path_to_file, "a+") as f:
        f.write(''.join('{}\t{}\n'.format(b_value, b_cords)))


def save_to_ecdf_data(pop_f_name, best_q_log, no):
    # meant for f7 2-dimensional q-function 
    dirname = os.path.dirname(__file__)
    filename = f"ecdf_data/{pop_f_name}_{no}.txt"
    path_to_file = os.path.join(dirname, filename)
    with open(path_to_file, "a+") as f:
        f.write(''.join('{}\n'.format(best_q_log)))


def calc_z_limits(q: Callable):
    z_limits = (0, 30)
    q_name = q.__name__
    if 'f' in q_name:
        z_lim = float(q_name[1:]) * 100.0
        z_limits = (z_lim - 100.0, z_lim + 300.0)
    return z_limits


# ALGORITHM
def initialise_algorithm(point_start: tuple, T_MAX: int,
                         pop_f: Callable, POP_MIN: int, POP_MAX: int,
                         q: Callable, mutation: Callable,
                         live_plot: DataVisualiser = None):
    pop, log = {}, {}
    pop_size = pop_f(0, T_MAX, POP_MIN, POP_MAX)
    log[point_start] = q(point_start)
    for i in range(pop_size):
        new_point = mutation(point_start)
        pop[new_point] = q(new_point)
        log[new_point] = q(new_point)

    if live_plot:
        init_plot_multiprocess(live_plot=live_plot, q=q, data=log)
        time.sleep(2.0)

    pop_size_log = [(0, pop_size)]
    best_q_log = [(0, min(log.values()))]

    return pop, log, pop_size_log, best_q_log


def algorithm(point_start: tuple, T_MAX: int, Q_MAX: int,
              pop_f: Callable, POP_MIN: int, POP_MAX: int,
              q: Callable, mutation: Callable, select: Callable,
              live_plot: DataVisualiser = None):
    # POPULATION INITIALISATION
    pop, log, pop_size_log, best_q_log = initialise_algorithm(point_start=point_start, T_MAX=T_MAX,
                                                              pop_f=pop_f, POP_MIN=POP_MIN, POP_MAX=POP_MAX,
                                                              q=q, mutation=mutation, live_plot=live_plot)

    new_pop = {}
    q_counter, t = 0, 1
    q_value, q_best_value, pop_size = None, None, None
    while True:

        pop_size = pop_f(t, T_MAX, POP_MIN, POP_MAX, q=q_best_value, current_pop_size=pop_size)

        # not allowing to use more than given destination function budget limit
        if q_counter + pop_size > Q_MAX:
            break

        t += 1
        q_best_value = numpy.inf
        for i in range(pop_size):
            new_point = mutation(select(pop))
            q_value = q(new_point)
            new_pop[new_point] = q_value
            log[new_point] = q_value
            q_counter += 1

            # remember best q_value in iteration for stagnation detection
            if q_value < q_best_value:
                q_best_value = q_value

        # append best q value in history for ecdf graph
        best_q_log.append((t-1, min(log.values())))
        # append pop size for population plot
        pop_size_log.append((t, pop_size))

        if live_plot:
            live_plot.set_data(data=new_pop)

        pop = new_pop
        new_pop = {}

    print(f"WYKORZYSTANY BUDŻET FUNKCJI CELU:{q_counter}\nLICZBA ITERACJI: {t - 1}")
    
    return log, pop_size_log, best_q_log


# PLOTTING
def init_plot_multiprocess(live_plot: DataVisualiser, q: Callable, data: dict or list):
    x_limits = y_limits = (-100, 100)
    z_limits = calc_z_limits(q=q)
    return live_plot.init_plot_multiprocess(main_title="Wizualizacja",
                                            data=data, data_color="red", data_size=1,
                                            q_func=q, q_domain=x_limits,
                                            q_points=120, q_alpha=1.0,
                                            x_limits=x_limits,
                                            y_limits=y_limits,
                                            z_limits=z_limits)


def make_plot_log(plot_type, q: Callable, data: dict or list):
    x_limits = y_limits = (-100, 100)
    z_limits = calc_z_limits(q=q)

    return DataVisualiser(plot_type=plot_type).init_plot(main_title="Wizualizacja",
                                                         data=data, data_color="red", data_size=1,
                                                         q_func=q, q_domain=x_limits, q_points=120,
                                                         q_alpha=0.2,
                                                         x_limits=x_limits, y_limits=y_limits,
                                                         z_limits=z_limits,
                                                         )


def make_plot_pop(pop_size_log: list[tuple, tuple], pop_min, pop_max):
    x_limits = (pop_size_log[0][0], pop_size_log[-1][0])
    y_limits = (pop_min, pop_max)

    return DataVisualiser(plot_type="2D").init_plot_multiprocess(main_title="Zmienność populacji", data=pop_size_log,
                                                                 x_limits=x_limits, y_limits=y_limits,
                                                                 try_connect_scatter=True)


def make_plot_ecdf(best_q_log: list,
                   _step_y: float, _from_y: float = None, _to_y: float = None,
                   _from_x: int = 0, _to_x: int = None):
    x_limits = (_from_x, _to_x if _to_x else len(best_q_log))
    _from_y = _from_y if _from_y else math.floor(min(best_q_log, key=lambda q: q[1])[1])
    _to_y = _to_y if _to_y else math.ceil(max(best_q_log, key=lambda q: q[1])[1])
    y_limits = (0, 1)

    bounds = numpy.linspace(_from_y, _to_y, int((_to_y - _from_y) / _step_y))
    target_count = len(bounds)

    ecdf_log = []
    # generating data for ecdf
    for (t, q) in best_q_log:
        val = 0.0
        if q <= bounds[0]:  # equal (or somehow better than) to minimum
            val = 1.0
        elif q > bounds[-1]:  # worse than the easiest target
            val = 0.0
        else:
            for i, (u_bound, l_bound) in enumerate(zip(reversed(bounds[:]), reversed(bounds[:-1]))):
                if u_bound >= q > l_bound:
                    val = (i + 1) / target_count
                    break

        ecdf_log.append((t, val))

    return DataVisualiser(plot_type="2D").init_plot_multiprocess(main_title="Krzywa ECDF", data=ecdf_log,
                                                                 x_limits=x_limits, y_limits=y_limits,
                                                                 data_size=0.0,
                                                                 try_connect_scatter=True)


# MAIN
def main(experiment_no=None):
    """
    plot parameters for q functions:
    f4 - optimum 400 -> x_limits = y_limits = (-100, 100), z_limits = (300, 600)
    f7 - optimum 700 -> x_limits = y_limits = (-100, 100), z_limits = (600, 900)
    ackley - optimum 0 -> x_limits = y_limits = (-100, 100), z_limits = (0, 30)

    z_limits automatically calculated in `calc_z_limits()` function
    """

    # INIT VARIABLES
    pop_min, pop_max = 1, 40  # to choose from (1, 40) or (5, 5) for constant
    dimensions = 2  # to choose from [2, 10, 20, 30, 50, 100]
    q_name = "f7"  # to choose from ['f4', 'f7', 'ackley']
    pop_f_name = "linear_increase"  # to choose from functions.population_functions
    q = get_function.q(function_name=q_name)
    pop_f = get_function.population(function_name=pop_f_name)

    # INIT CONST VALUES
    _Q_MAX = 20000  # BUDŻET FUNKCJI CELU
    _SELECT_F_NAME = "tournament_selection_min"
    _MUTATION_F_NAME = "gaussian_mutation"
    _SELECT = get_function.selection(function_name=_SELECT_F_NAME)
    _MUTATION = get_function.mutation(function_name=_MUTATION_F_NAME)
    _START_CORD = 50
    _POINT_START = tuple([_START_CORD for _ in range(dimensions)])

    # PLOT SETTINGS
    live_plot = False

    # if live_plot is True, following will have no effect:
    plot_log = False
    plot_pop = False
    plot_ecdf = False

    # PROPER ALGORITHM (WITH LIVE PLOT IF DEFINED)
    with DataVisualiser(plot_type="3D") if live_plot else nullcontext() as live_plot:
        t_max = get_t_max(Q_MAX=_Q_MAX, pop_f=pop_f, POP_MIN=pop_min, POP_MAX=pop_max)

        log, pop_size_log, best_q_log = algorithm(point_start=_POINT_START, T_MAX=t_max, Q_MAX=_Q_MAX,
                                                  pop_f=pop_f, POP_MIN=pop_min, POP_MAX=pop_max,
                                                  q=q, mutation=_MUTATION, select=_SELECT, live_plot=live_plot)
        save_to_ecdf_data(pop_f_name, best_q_log, experiment_no)

    # ADDITIONAL PLOTTING (IF LIVE PLOT NOT DEFINED)
    if not live_plot and (plot_log or plot_pop or plot_ecdf):
        __plot_pop, __plot_ecdf = None, None
        if plot_pop:
            __plot_pop = make_plot_pop(pop_size_log=pop_size_log, pop_min=pop_min, pop_max=pop_max)
        if plot_ecdf:
            __plot_ecdf = make_plot_ecdf(best_q_log=best_q_log, _step_y=1.0, _from_y=400.0, _to_y=430.0,
                                         _from_x=0, _to_x=t_max)
        if plot_log:
            make_plot_log(plot_type="3D", q=q, data=log)

        __plot_pop.join() if __plot_pop else None
        __plot_ecdf.join() if __plot_ecdf else None


if __name__ == "__main__":
    for no in range(25):
        main(no+1)
