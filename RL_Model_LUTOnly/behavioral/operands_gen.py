#This function generates operands
from fixedpoint import FixedPoint as fxp
import numpy as np
def operands(bit_width):
    operand_list = [[] for i in range(int(np.power(2,bit_width)*np.power(2,bit_width)))]
    list_ind = 0
    for op1 in range (-1*pow(2,bit_width-1),pow(2,bit_width-1)): # op1 is multiplicand
        for op2 in range (-1*pow(2,bit_width-1),pow(2,bit_width-1)):  # op2 is multiplier
            operand_list[list_ind].append(op1)
            operand_list[list_ind].append(op2)
            list_ind = list_ind+1

    return operand_list
