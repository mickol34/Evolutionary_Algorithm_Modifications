import os
import statistics


def read_data(q_name, pop_f_name, dims):
    dirname = os.path.dirname(__file__)
    filename = f"data/{q_name}_{pop_f_name}_{dims}.txt"
    path_to_file = os.path.join(dirname, filename)
    values = []
    cords = []
    with open(path_to_file, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            line = line.split("\t")
            values.append(float(line[0]))
            cords.append(eval(line[1]))
    min_value = round(min(values), 3)
    mean = round(statistics.mean(values), 3)
    std_dev = round(statistics.stdev(values), 3)
    return min_value, mean, std_dev


q_name = "ackley"
dimensions = 2
# pop_f_name = "linear_increase"
# pop_f_name = "linear_decrease"
# pop_f_name = "exponential_increase"
# pop_f_name = "exponential_decrease"
# pop_f_name = "sin_wave_change"
# pop_f_name = "rect_wave_change"
pop_f_names = ["linear_increase", "linear_decrease", "exponential_increase", "exponential_decrease", "sin_wave_change", "rect_wave_change", "rect_wave_change_on_stagnation", "const"]
for pop_name in pop_f_names:
    print(pop_name + " = \t" + str(read_data(q_name, pop_name, dimensions)))

# print(read_data(q_name, pop_f_name, dimensions))

# wartosc minimalna, wartosc srednia, odchylenie standardowe
# wstawic do tabeli
