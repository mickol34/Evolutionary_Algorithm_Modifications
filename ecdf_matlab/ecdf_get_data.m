% najmniejsza ilość iteracji dla funkcji reset: 987 (+1)

pop_f_names = ["constant", "linear_increase", "linear_decrease", "exponential_increase", "exponential_decrease", "sin_wave_change", "rect_wave_change", "rect_wave_change_on_stagnation"];
pop_f_mean_runs_vectors_map = containers.Map("KeyType", "char", "ValueType", "any");
pop_f_results_vectors_map = containers.Map("KeyType", "char", "ValueType", "any");

for pop_f_no = 1:length(pop_f_names)

    pop_f_name = pop_f_names(pop_f_no);

    %% Mean performance
    pop_f_sum = 0;
    if pop_f_name == "rect_wave_change_on_stagnation"
        for i = 1:25
            temp_vector = readmatrix(strcat("..\ecdf_data\", string(pop_f_name), "_", string(i), ".txt"), "Whitespace", "[] ()");
            temp_matrix = reshape(temp_vector, 2, length(temp_vector)/2);
            pop_f_sum = pop_f_sum + temp_matrix(2, 1:988);
        end
    else
        for i = 1:25
            temp_vector = readmatrix(strcat("..\ecdf_data\", string(pop_f_name), "_", string(i), ".txt"), "Whitespace", "[] ()");
            temp_matrix = reshape(temp_vector, 2, length(temp_vector)/2);
            pop_f_sum = pop_f_sum + temp_matrix(2, :);
        end
    end
    pop_f_sum = pop_f_sum/25;
    pop_f_mean_runs_vectors_map(pop_f_name) = ceil(pop_f_sum);

    %% Results
    if pop_f_name == "constant"
        pop_f_name_ = "const";
    else
        pop_f_name_ = pop_f_name;
    end
    temp_table = readtable(strcat("..\data\f7_", pop_f_name_, "_2.txt"));
    pop_f_results_vectors_map(pop_f_name) = sort(temp_table.Var1(1:25));
end

% !!ręczny save