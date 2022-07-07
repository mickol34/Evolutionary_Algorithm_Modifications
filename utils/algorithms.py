import heapq
from math import ceil

from scipy import integrate
from scipy.optimize import fsolve


def max_value_points_from_dictionary(points_dict: dict, number_of_best: int):
    return heapq.nlargest(number_of_best, points_dict, key=lambda x: points_dict[x])


def min_value_points_from_dictionary(points_dict: dict, number_of_best: int):
    return heapq.nsmallest(number_of_best, points_dict, key=lambda x: points_dict[x])


def get_t_max(Q_MAX, pop_f, POP_MIN, POP_MAX):
    """
    Function to get number of iterations (T_MAX) depending on given destination function budget limit (Q_MAX)
    and chosen population function (pop_f).
    Solves an equation:
                        ∫ [0 -> T_MAX] { pop_f(t) dt } = Q_MAX    -----     T_MAX = ?
    Parameters
    ----------
    Q_MAX: int - destination function budget limit
    pop_f: func - population function
    POP_MIN: int - minimum population (pop_f parameter)
    POP_MAX: int - max population (pop_f parameter)

    Returns
    -------
    T_MAX: int - number of algorithm iterations
    """

    # these methods do not need t_max
    if pop_f.__name__ in ("sin_wave_change", "rect_wave_change_on_stagnation"):
        return None

    def integrand(t, T_MAX):
        return pop_f(t, T_MAX, POP_MIN, POP_MAX)

    def func(T_MAX):
        y, err = integrate.quad(func=integrand, a=1, b=T_MAX, args=(T_MAX,), limit=1000)
        return y - Q_MAX

    sol = fsolve(func, Q_MAX/POP_MAX)
    return ceil(sol[0]) if sol else None
