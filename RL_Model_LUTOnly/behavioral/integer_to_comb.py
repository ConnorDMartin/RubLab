def integer_to_combination(integer_value, N):
    possible_values = ['E', 'O', 'Z']
    num_values = len(possible_values)
    combination = []

    for _ in range(N):
        position_value = integer_value % num_values
        # combination.append(possible_values[position_value])
        combination.insert(0, possible_values[position_value])
        integer_value //= num_values

    combination = ''.join(combination)

    return combination
