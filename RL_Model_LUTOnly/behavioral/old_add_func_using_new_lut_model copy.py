from fixedpoint import FixedPoint as fxp
import numpy as np
from behavioral.new_lut_model import LUT
# from new_lut_model import LUT
from pathlib import Path
import csv
from behavioral.operands_gen import operands
# from operands_gen import operands
import os
import itertools # for generating binary strings for dropping LUTs
from behavioral.integer_to_comb import integer_to_combination
# from integer_to_comb import integer_to_combination
import re
from multiprocessing import Pool


def adder(input_port_assignments, lut_string_inst, Lut_INIT_List, bit_width, arg1, arg2, enabled, testing_data):

    # bit_width = 8

    # lut_string_value_temp = integer_to_combination(lut_string_inst, bit_width)
    # lut_string_value = lut_string_value_temp[::-1]
    # enabled.reverse()
    # # For testing ///
    # print(lut_string_value)
    # print(enabled)
    # lut_string_value = ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']

    # lut_string_value_digit = [1 if value == 'E' else 0 for value in lut_string_value]

    result_dir = './../run_results/designs/v3/{}'.format(lut_string_inst)
    Path("{}".format(result_dir)).mkdir(parents=True, exist_ok=True)

    # file_new = open("{}/add_behv_v3_{}.csv".format(result_dir, lut_string_inst),"w")
    # writer = csv.writer(file_new)
    # header1 = ['a', 'b', 'approx']
    # writer.writerow(header1)

    operand_list = operands(bit_width=bit_width)

    # print(operand_list)
    operand_list = [[arg1, arg2]]
    list_ind = 0
    lut_list = []
    pps_list = []
    error_total = 0
    iteration = 0


    for mtd in range(0, bit_width):
        lut_list.append(LUT(Lut_INIT_List[mtd]))


            # If bit enabled, set as valid. Else, set as zero
        if enabled[mtd]:
            lut_list[mtd].set_valid('E')
        else:
            lut_list[mtd].set_valid('Z')


    # with open("testing_values.csv","r",newline='') as state_file:
    # with open("testing_values.csv","r",newline='') as state_file:
        # reader = csv.reader(state_file)
        # pattern = r"[0-9]+"

    args = []
    num_slices = 10

    # calc_error_wrapper(data_slice, bit_width, input_port_assignments, lut_list)

    slice_width = len(testing_data) // num_slices

    current_indx = 0
    for i in range(num_slices):
        args.append((testing_data[current_indx:current_indx + slice_width] , bit_width, input_port_assignments, lut_list))
        current_indx = current_indx + slice_width
    

    with Pool(processes=num_slices) as pool:
        results = pool.starmap(calc_error_wrapper, args)

    error_total = np.sum(results)


    return error_total/len(testing_data)
    # return error_total/error_count




    # for op in operand_list:
    #     op1= op[0]
    #     op2= op[1]
    #     # print(bin(op1))
    #     # print(bin(op2))

    #     op1_bin_temp = str(fxp(op1, m=bit_width, str_base=2))
    #     op2_bin_temp = str(fxp(op2, m=bit_width, str_base=2))

    #     op1_bin = [L[::-1] for L in op1_bin_temp] # to reverse the list for easy access
    #     op2_bin = [L[::-1] for L in op2_bin_temp]


    #     op1_bin.reverse()
    #     op2_bin.reverse()
    #     # convert list of str to list of int
    #     op1_bin = [1 if value == '1' else 0 for value in op1_bin]
    #     op2_bin = [1 if value == '1' else 0 for value in op2_bin]
    #     # print(op1_bin)
    #     # print(op2_bin)



    #     ## From Prev Implementation: 

    #     # lut_list.append(LUT(Lut_INIT_List[0])) # Provide INIT value of the LUT
    #     # lut_list[0].set_valid(lut_string_value[0]) # Status of LUT: Enabled, Disabled


    #     # # Provide inputs to compute O5 and O6 if LUT is enabled.

    #     # lut_list[0].get_lut_outputs(op1_bin[0], op2_bin[0],op1_bin[1], op2_bin[1],lut_string_value_digit[1],1)

    #     # # Perform addition to compute sum and carry bit. Initial cin is 0.
    #     # lut_list[0].get_sum_carry(0)


    #     # # Repeat for remaining LUTs.
    #     # # Last (MSB) LUT is different
    #     # for mtd in range(1, bit_width-1):
    #     #     lut_list.append(LUT(Lut_INIT_List[mtd]))
    #     #     lut_list[mtd].set_valid(lut_string_value[mtd])
    #     #     lut_list[mtd].get_lut_outputs(op1_bin[mtd], op2_bin[mtd],op1_bin[mtd+1], op2_bin[mtd+1],lut_string_value_digit[mtd+1],1)
    #     #     lut_list[mtd].get_sum_carry(lut_list[mtd-1].cout)

    #     # lut_list.append(LUT(Lut_INIT_List[bit_width-1]))
    #     # lut_list[bit_width-1].set_valid(lut_string_value[bit_width-1])
    #     # lut_list[bit_width-1].get_lut_outputs(op1_bin[bit_width-1], op2_bin[bit_width-1],0, 0,0,1)
    #     # lut_list[bit_width-1].get_sum_carry(lut_list[bit_width-2].cout)

    #     ## New Implementation: 
            
    #         assignments = input_port_assignments[mtd]
    #         in_a = find_input(5, assignments, op1_bin, op2_bin)
    #         in_b = find_input(4, assignments, op1_bin, op2_bin)
    #         in_c = find_input(3, assignments, op1_bin, op2_bin)
    #         in_d = find_input(2, assignments, op1_bin, op2_bin)
    #         in_e = find_input(1, assignments, op1_bin, op2_bin)
    #         in_f = find_input(0, assignments, op1_bin, op2_bin)
    #         # print(in_a, in_b, in_c, in_d, in_e, in_f)
    #         # print(hex(Lut_INIT_List[mtd]))
    #         lut_list[mtd].get_lut_outputs(in_a, in_b, in_c, in_d, in_e, in_f)
    #         lut_list[mtd].get_sum_carry(lut_list[mtd-1].cout)
    #         # print("Cout: "+str(lut_list[mtd].cout))

    #     for i in range(len(lut_list)):
    #         pps_list.insert(0, lut_list[i].sum)
    #         if i == len(lut_list)-1:
    #             pps_list.insert(0, lut_list[i].cout)

    #     # print(pps_list)

    #     pps_int = []
    #     sum = 0 # to store the sum
    #     num_elem = len(pps_list) # to find power of 2, I need maximum number of elements

    #     for elem in pps_list:   # access elements of sub_list
    #         num_elem = num_elem - 1
    #         if num_elem == len(pps_list)-1:
    #             sum = sum - elem * np.power(2, num_elem)
    #         else:
    #             sum = sum + elem * np.power(2, num_elem)

    #     # writer.writerow([op[0], op[1], sum])
    # # file_new.close()
    # # print(bin(sum))
    # error = sum - real_result

    # error_total += error
    # error_count += 1

    # iteration += 1

    # return error_total/error_count
# Lut_INIT_List = [0x6666666688888888, 0x6666666688888888, 0x6666666688888888, 0x6666666688888888, 0x6666666688888888, 0x6666666688888888, 0x6666666688888888, 0x6666666688888888]
# adder (0, Lut_INIT_List, 8)

def find_input(x, assignments, op1_bin, op2_bin):
    op = assignments[x][0]
    op_bit = assignments[x][1]

    if op == 1:
        return op1_bin[op_bit]
    elif op == 2:
        return op2_bin[op_bit]
    else:
        return op_bit
    
def calc_error_wrapper(data_slice, bit_width, input_port_assignments, lut_list):
    iteration = 0
    while iteration < len(data_slice):
        # args = []
        error_total = 0

        # error = calc_error(arg1, arg2, iteration, bit_width, input_port_assignments, lut_list)
        for i in range(10):
            curr_iter = iteration + i
            arg1 = data_slice[curr_iter][0]
            arg2 = data_slice[curr_iter][1]
            # args.append((arg1, arg2, iteration + i, bit_width, input_port_assignments, lut_list))

            error_total += calc_error(arg1, arg2, iteration + i, bit_width, input_port_assignments, lut_list)


        # with Pool(processes=10) as pool:
        #     results = pool.starmap(calc_error, args)

        # error_total = np.sum(results)

        iteration += 10

    return error_total


def calc_error(arg1, arg2, iteration, bit_width, input_port_assignments, lut_list):
        # if (iteration == 250) or (iteration == 500) or (iteration == 750) or (iteration == 999):
        #     print(".")

        # arg1, arg2 = re.findall(pattern, str(row))

        # print(arg1)
        # print(arg2)
        arg1 = int(arg1)
        arg2 = int(arg2)
        # print("lut: " +str(lut_result))
        real_result = arg1 + arg2
        # print("real: " + str(real_result))
        op1 = arg1
        op2 = arg2
        pps_list = []

        # print("Arg1: "+str(arg1))
        # print("Arg2: "+str(arg2))

        op1_bin_temp = str(fxp(op1, m=bit_width, str_base=2))
        op2_bin_temp = str(fxp(op2, m=bit_width, str_base=2))

        op1_bin = [L[::-1] for L in op1_bin_temp] # to reverse the list for easy access
        op2_bin = [L[::-1] for L in op2_bin_temp]


        op1_bin.reverse()
        op2_bin.reverse()
        # convert list of str to list of int
        op1_bin = [1 if value == '1' else 0 for value in op1_bin]
        op2_bin = [1 if value == '1' else 0 for value in op2_bin]


        for mtd in range(0, bit_width):
            assignments = input_port_assignments[mtd]
            in_a = find_input(5, assignments, op1_bin, op2_bin)
            in_b = find_input(4, assignments, op1_bin, op2_bin)
            in_c = find_input(3, assignments, op1_bin, op2_bin)
            in_d = find_input(2, assignments, op1_bin, op2_bin)
            in_e = find_input(1, assignments, op1_bin, op2_bin)
            in_f = find_input(0, assignments, op1_bin, op2_bin)
            # print(in_a, in_b, in_c, in_d, in_e, in_f)
            # print(hex(Lut_INIT_List[mtd]))
            lut_list[mtd].get_lut_outputs(in_a, in_b, in_c, in_d, in_e, in_f)
            lut_list[mtd].get_sum_carry(lut_list[mtd-1].cout)
            # print("Cout: "+str(lut_list[mtd].cout))

        for i in range(len(lut_list)):
            pps_list.insert(0, lut_list[i].sum)
            if i == len(lut_list)-1:
                pps_list.insert(0, lut_list[i].cout)

        # print(pps_list)

        pps_int = []
        sum = 0 # to store the sum
        num_elem = len(pps_list) # to find power of 2, I need maximum number of elements

        for elem in pps_list:   # access elements of sub_list
            num_elem = num_elem - 1
            if num_elem == len(pps_list)-1:
                sum = sum - elem * np.power(2, num_elem)
            else:
                sum = sum + elem * np.power(2, num_elem)

        # print(sum)
        # print(real_result)
        error = sum - real_result

        return error




# input_port_assignments = [[[0, 1], [0, 0], [0, 0], [0, 0], [2, 0], [1, 0]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 1], [1, 1]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 2], [1, 2]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 3], [1, 3]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 4], [1, 4]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 5], [1, 5]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]]]
# lut_string_inst = 0
# Lut_INIT_List = [7378697630056482952, 7378697630056482952, 7378697630056482952, 7378697630056482952, 7378697630056482952, 7378697630056482952, 7378697630056482952, 7378697630056482952]
# bit_width = 8
# arg1 = 0b00000011
# arg2 = 0b00000001
# enabled = [1, 1, 1, 1, 1, 1, 1, 1]
# print(adder(input_port_assignments, lut_string_inst, Lut_INIT_List, bit_width, arg1, arg2, enabled))