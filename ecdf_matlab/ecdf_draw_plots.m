% rozdzielone na dwa pliki, aby nie musieć ładować za każdym razem danych

runs_load = load("pop_f_mean_runs_vectors_map.mat");
results_load = load("pop_f_results_vectors_map.mat");

pop_f_mean_runs_vectors_map = runs_load.pop_f_mean_runs_vectors_map;
pop_f_results_vectors_map = results_load.pop_f_results_vectors_map;

pop_f_names = ["constant", "linear_increase", "linear_decrease", "exponential_increase", "exponential_decrease", "sin_wave_change", "rect_wave_change", "rect_wave_change_on_stagnation"];

%% ECDF
figure
hold on
grid on
for i = 1:length(pop_f_names)
    if i<=4
        plot(pop_f_mean_runs_vectors_map(pop_f_names(i)))
    else
        plot(pop_f_mean_runs_vectors_map(pop_f_names(i)), "--")
    end
end
legend(strrep(pop_f_names, "_", " "))
title("Zestawienie krzywych ECDF")
print("zestawienie_krzywych_ecdf_bez_przycinania.png", "-dpng", "-r280")
xlim([0 1000])
print("zestawienie_krzywych_ecdf_po_przycieciu.png", "-dpng", "-r280")

%% Dystrybuanta
figure
hold on
grid on
for i = 1:length(pop_f_names)
    x_axis = pop_f_results_vectors_map(pop_f_names(i));
    y_axis = [0:1/24:1];
    if i<=4
        plot(x_axis, y_axis)
    else
        plot(x_axis, y_axis, "--")
    end
end
legend(strrep(pop_f_names, "_", " "), "Location", "southeast")
title("Dystrybuanty empiryczne")
print("dystrybuanty_empiryczne.png", "-dpng", "-r280")


