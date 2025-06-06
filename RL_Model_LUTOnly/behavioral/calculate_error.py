from behavioral.add_func_using_new_lut_model import adder
# from add_func_using_new_lut_model import adder
import csv
import re
import numpy as np

def get_error(state):
    enabled = []
    input_port_assignments = []
    Lut_INIT_List = []
    lut_string_inst = 0
    bit_width = 8

    # np.array(state).flatten()
    # print(state)
    state = np.array(state)
    state = state.reshape(8, 77)

    for s_ in state:
        # convert binary value of LUT init code to hex
        # print(s_)

        init_code = 0
        for t_ in range(64):
            # print(s_[63 - t_])
            # print(2 ** t_)
            init_code += s_[t_] << (63 - t_)

        # print(init_code)
        Lut_INIT_List.append(init_code)
        # Lut_INIT_List.append(0x6666666688888888)
        # print("init code is: " + hex(init_code))

        # compile input port assignments
        t_ = 64
        input_port_list = []
        while t_ < 76:
            input_port_list.append([int(s_[t_]), int(s_[t_+1])])
            t_ += 2
        input_port_assignments.append(input_port_list)

        # compile list of enabled/disabled LUTs
        enabled.append(int(s_[-1]))


    error_total = 0
    error_count = 0
    arg1 = 0
    arg2 = 0

    return adder(input_port_assignments, lut_string_inst, Lut_INIT_List, bit_width, arg1, arg2, enabled)

    # with open("../testing_values.csv","r",newline='') as state_file:
    # # with open("testing_values.csv","r",newline='') as state_file:
    #     reader = csv.reader(state_file)
    #     pattern = r"[0-9]+"

    #     iteration = 0
    #     for row in reader:
    #         if (iteration == 250) or (iteration == 500) or (iteration == 750) or (iteration == 999):
    #             print(".")

    #         arg1, arg2 = re.findall(pattern, str(row))
    #         # print(arg1)
    #         # print(arg2)
    #         arg1 = int(arg1)
    #         arg2 = int(arg2)

    #         lut_result = adder(input_port_assignments, lut_string_inst, Lut_INIT_List, bit_width, arg1, arg2, enabled)
    #         # print("lut: " +str(lut_result))
    #         real_result = arg1 + arg2
    #         # print("real: " + str(real_result))

    #         error = lut_result - real_result

    #         error_total += error
    #         error_count += 1

    #         iteration += 1

    # return error_total/error_count

def preprocess_state(state):
    processed = []
    for lut in state:
        init_code = lut[0]
        port_assignments = np.array(lut[1]).flatten() #flatten 6x2 -> [12]
        enabled_flag = np.array([lut[2]]) #convert integer to array

        #convert init code to binary representation
        binary_str = format(init_code, 'b')
        padded_binary_str = binary_str.zfill(64)
        init_code_bits = np.array([int(bit) for bit in padded_binary_str])

        #concatenate features
        lut_features = np.concatenate([init_code_bits, port_assignments, enabled_flag])
        processed.append(lut_features)
    return np.array(processed)


input_state = [[0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 0], [1, 0]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 1], [1, 1]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 2], [1, 2]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 3], [1, 3]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 4], [1, 4]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 5], [1, 5]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]], 1]]
input_state = preprocess_state(input_state)
print(get_error(input_state))