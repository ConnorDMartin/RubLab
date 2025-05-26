# This is the top function to implement multiplier
from fixedpoint import FixedPoint as fxp
import numpy as np
from operands_gen import operands
from add_func_LUT_new import add
import itertools # for generating binary strings for dropping LUTs
from pathlib import Path
import csv
import os
from shutil import copyfile
import random
from integer_to_comb import integer_to_combination
import pandas as pd

random.seed(a=0)
trial = 1 # first run was 1

bit_width = 8
version = 'v2'

# retrieve current LUT config from current state file
# state_file = open("../current_state.csv","r")
with open("../current_state.csv","r") as state_file:
    state_data = []
    reader = csv.reader(state_file)
    for row in reader:
        int_row = [int(item) for item in row]
        state_data.append(int_row)
    run_iter = state_data[-1][0]
    state_data.pop(-1)
    print(state_data)




max_comb = (3**bit_width)

called_dir = Path().absolute()
file_lut_config = open("{}/testConfigs.sh".format(called_dir) ,"w")
file_lut_config.write('arr_configs=(')

# lut_string_total = random.sample(range(max_comb), max_comb)
lut_string_total = [run_iter]
lut_string = lut_string_total
# possible_values = ['E', 'O', 'Z']
# Therefore, EEE maps to 0 which refers to an accurate implementation
### Write to a file all values
file_new = open("./eoz_values.csv","w")
writer = csv.writer(file_new)
header1 = ['integer', 'binary', 'eoz']
writer.writerow(header1)

## modify this to represent LUT states
for i in range(len(lut_string)):
    lut_string_inst = lut_string[i]

    lut_string_value_temp = integer_to_combination(lut_string_inst, bit_width)
    lut_string_value = lut_string_value_temp[::-1]
    lut_string_value_binary = ['1' if value == 'E' else '0' for value in lut_string_value]

    writer.writerow([lut_string_inst, lut_string_value_binary, lut_string_value])

file_new.close()

## Load the csv file again to find the valid configurations
df = pd.read_csv('./eoz_values.csv')
# Extract records where the rightmost two characters of 'eoz' column are not 'E'
extracted_records = df[~df['eoz'].str[-2:].eq('EE')]

# Store the extracted records in a separate CSV file
extracted_records.to_csv('./extracted_records_no_E.csv', index=False)

# Store the corresponding 'integer' values of the extracted records in a separate CSV file
integer_values = extracted_records['integer']
integer_values.to_csv('./integer_values_no_E.csv', index=False, header=['integer'])

# Get a list of the 'integer' values of the extracted records without the header
integer_values_list = extracted_records['integer'].tolist()
# print(integer_values_list)

print('total extracted records: ', len(integer_values_list))


print('lut_string before: ', len(lut_string))


all_zeros = integer_values_list

for all_zeros_item in all_zeros:
    if all_zeros_item in lut_string:
        lut_string.remove(all_zeros_item)

print('new_configs after removing all ones and zeros: ', len(lut_string))

# New variable parsing based on LUT state passed from rl_model.py
enabled = []
input_port_assignments = []
Lut_INIT_List = []
lut_string_inst = 0
bit_size = 8
for s_ in state_data:
    # convert binary value of LUT init code to hex
    t_ = 63
    init_code = 0
    while t_ >= 0:
        init_code += s_[63 - t_] * (2 ** t_)
        t_ -= 1
    print(init_code)
    init_code = hex(init_code)
    Lut_INIT_List.append(init_code)

    # compile input port assignments
    t_ = 64
    input_port_list = []
    while t_ < 76:
        input_port_list.append([s_[t_], s_[t_+1]])
        t_ += 2
    input_port_assignments.append(input_port_list)

    # compile list of enabled/disabled LUTs
    enabled.append(s_[-1])

# ## Check if for loop is necessary
# for i in range(len(lut_string)):

#     lut_string_inst = lut_string[i]

    # add(bit_width=bit_width, lut_string_inst=lut_string_inst, version=version)

print(bit_size)
print(lut_string_inst)
print(Lut_INIT_List)
print(input_port_assignments)
print(enabled)
add(bit_size, lut_string_inst, Lut_INIT_List, input_port_assignments, enabled)
called_dir = Path().absolute()
result_dir = './../results/designs/{}/{}'.format(version, lut_string_inst)


file_lut_config.write('{}\n'.format(lut_string_inst))

file_lut_config.write(')'.format(lut_string_inst))

file_lut_config.close()
state_file.close()


'''
Clean up and debug this program, lots of uneeded code here and an uneeded input in add_func_LUT_new.py
'''