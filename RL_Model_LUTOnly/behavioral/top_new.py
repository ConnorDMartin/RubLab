# This is the top function to implement multiplier
from fixedpoint import FixedPoint as fxp
import numpy as np
from operands_gen import operands
from pathlib import Path
import os
from add_func_using_new_lut_model import adder
import itertools # for generating binary strings for dropping LUTs
import csv
import random
from multiprocessing import Pool
import multiprocessing


random.seed(a=0)
trial = 1 # first run was 1

current_dir = Path(__file__).parent.absolute()
called_dir = Path().absolute()
os.chdir(str(current_dir))

bit_width = 8

operand_list = operands(bit_width=bit_width)

max_configs = 1024
# max_configs = (2**bit_width)
max_comb = (3**bit_width)
max_configs_new = trial * max_configs


lut_string_total = random.sample(range(max_comb), max_configs_new)
lut_string = lut_string_total
# possible_values = ['E', 'O', 'Z']
# Therefore, EEE maps to 0 which refers to an accurate implementation
corner_cases = [0]
print('lut_string before: ', len(lut_string))
for corner in corner_cases:
    if (corner in lut_string) == False:
        lut_string.append(corner)

print('new_configs: ', len(lut_string))

# lut_string = [15]
# lut_string = [255, 254, 1]
all_ones = int(((3**bit_width)-1)/2)
all_zeros = int(((3**bit_width)-1))
if all_ones in lut_string:
    lut_string.remove(all_ones)

if all_zeros in lut_string:
    lut_string.remove(all_zeros)

print('new_configs after removing all ones and zeros: ', len(lut_string))


p = multiprocessing.Pool(16)
p.map(adder, lut_string)
p.close()
p.join()


os.chdir(str(called_dir))
