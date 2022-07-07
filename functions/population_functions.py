import math

def linear_increase(t, t_max, pop_min, pop_max, **kwargs):
    return math.floor(pop_min + ((pop_max - pop_min) * t / t_max))


def linear_decrease(t, t_max, pop_min, pop_max, **kwargs):
    return math.floor(pop_max - ((pop_max - pop_min) * t / t_max))


def exponential_increase(t, t_max, pop_min, pop_max, **kwargs):
    base = math.pow(pop_max / pop_min, 1 / t_max)
    return min(math.floor(pop_min * (pow(base, t))), pop_max)


def exponential_decrease(t, t_max, pop_min, pop_max, **kwargs):
    base = math.pow(pop_min / pop_max, 1 / t_max)
    return max(math.floor(pop_max * (pow(base, t))), pop_min)


def sin_wave_change(t, t_max, pop_min, pop_max, **kwargs):
    slow_coeff = 10  # constant
    rang = (pop_max - pop_min) / 2
    return math.floor(pop_min + rang + rang * math.sin(t / slow_coeff))


def rect_wave_change(t, t_max, pop_min, pop_max, **kwargs):
    step_width = math.floor(t_max / 10)  # constant
    if t % (2 * step_width) < step_width:
        pop = pop_min
    else:
        pop = pop_max
    return pop


def __stagnation_checker_generator(q_keep, q_tol):
    q_log = []

    while True:
        # acquire current q value
        q = yield

        # initialisation or no stagnation detected
        if (len(q_log) < q_keep) or (abs(q - (sum(q_log) / q_keep)) > q_tol):
            # save current q value
            if len(q_log) < q_keep:
                q_log.append(q)
            else:
                q_log = [*q_log[1:], q]
            yield False


        # stagnation detected!
        else:
            q_log = []
            yield True


# STAGNATION GENERATOR INITIALISATION
stagnation_checker_generator = __stagnation_checker_generator(q_keep=50, q_tol=0.5)


def rect_wave_change_on_stagnation(t, t_max, pop_min, pop_max, q=None, current_pop_size=None, **kwargs):
    if q is None or current_pop_size is None:
        return pop_min

    if current_pop_size != pop_min and current_pop_size != pop_max:
        raise Exception("current_pop_size must be equal to either pop_max or pop_min")

    next(stagnation_checker_generator)
    stagnate = stagnation_checker_generator.send(q)

    if not stagnate:
        return current_pop_size

    if current_pop_size == pop_min:
        return pop_max

    elif current_pop_size == pop_max:
        return pop_min


if __name__ == "__main__":
    pop_f = rect_wave_change_on_stagnation
    current_pop_size = 10
    for i in range(30):
        new_pop_size = pop_f(0, 0, 0, 10, q=5, current_pop_size=current_pop_size)
        print(new_pop_size)
        current_pop_size = new_pop_size
