# This function implements a multiplier using baugh-Wooley Algorithm
from fixedpoint import FixedPoint as fxp
import numpy as np
from pathlib import Path
import os

from integer_to_comb import integer_to_combination

def add(bit_width, lut_string_inst, lut_init_list, input_port_assignments, enabled):

    # if version == 'v1':
    #     INIT_version = "6666666688888888"
    # elif version == 'v2':
    #     INIT_version = "666606608888F880"
    # elif version == 'v3':
    #     INIT_version = "666606668888F880"

    #print(type(lut_string_inst))
    current_dir = Path(__file__).parent.absolute()
    called_dir = Path().absolute()
    os.chdir(str(current_dir))
    result_dir = './results/designs/{}'.format(lut_string_inst)

    lut_string_value_temp = integer_to_combination(lut_string_inst, bit_width)
    lut_string_value = lut_string_value_temp[::-1]
    lut_string_value_binary = ['1' if value == 'E' else '0' for value in lut_string_value]

    #

    # print(current_dir)
    Path("{}".format(result_dir)).mkdir(parents=True, exist_ok=True)
    file = open('{}/adder_{}.vhd'.format(result_dir,lut_string_inst), 'w')
    print(file)
    file.write('-- Scripted code by salim.ullah@tu-dresden.de')
    file.write('-- Receives 3 values E O Z for every location \n')
    file.write('-- MSB is accurate')
    file.write('\n')

    file.write('library IEEE; \n')
    file.write('use IEEE.STD_LOGIC_1164.ALL; \n')
    file.write('use IEEE.NUMERIC_STD.ALL; \n')
    file.write('use IEEE.STD_LOGIC_SIGNED.ALL; \n')
    file.write('library UNISIM; \n')
    file.write('use UNISIM.VComponents.all; \n')

    file.write('\n')

    file.write('entity adder is \n')
    file.write('generic (word_size: integer:='+str(bit_width)+'); \n')
    file.write('Port ( \n')
    file.write('a : in  STD_LOGIC_VECTOR (word_size-1 downto 0); \n')
    file.write('b : in  STD_LOGIC_VECTOR (word_size-1 downto 0); \n')
    file.write('sum: out STD_LOGIC_VECTOR (word_size-1 downto 0)); \n')
    file.write('end adder; \n')
    #
    file.write('\n')
    file.write('architecture Behavioral of adder is \n')
    file.write('\n')

    file.write('constant slice_size :integer := ((word_size + 4 - 1)/4)*4; \n')
    file.write('signal prop, gen: std_logic_vector(slice_size-1 downto 0); \n')
    file.write('signal carries: std_logic_vector(slice_size-1 downto 0); \n')
    file.write('signal output: std_logic_vector(slice_size-1 downto 0); \n')
    file.write('signal input_carry: std_logic_vector(word_size-1 downto 0); \n')

    file.write('\n')
    file.write('begin \n \n ')

    file.write("input_carry(0) <= '0'; \n")


    for mlr in range(0, bit_width):

        # if (mlr != bit_width-1):

        #     if (mlr != bit_width-2):
                assignments = input_port_assignments[mlr]
                in_a = find_input(5, assignments)
                in_b = find_input(4, assignments)
                in_c = find_input(3, assignments)
                in_d = find_input(2, assignments)
                in_e = find_input(1, assignments)
                in_f = find_input(0, assignments)
                # if (lut_string_value[mlr] == 'E'):
                file.write('lut_inst_'+str(mlr)+': lut6_2 \n')
                file.write('\n generic map(INIT => X"' + str(lut_init_list[mlr])[1:] + '") \n')
                # file.write('\n generic map(INIT => X"666606668888F880") \n')
                file.write('port map( \n')
                file.write('I0 => '+in_a+',  \n')
                file.write('I1 => '+in_b+',  \n')
                file.write('I2 => '+in_c+',  \n')
                file.write('I3 => '+in_d+',  \n')
                file.write('I4 => '+in_e+',  \n')
                file.write('I5 => '+in_f+',  \n')
                file.write('O5 => gen('+str(mlr)+'), \n')
                file.write('O6 => prop('+str(mlr)+') \n')
                file.write('); \n')
                # else:
                #     file.write("gen("+str(mlr)+") <= '0' ;\n")
                #     file.write("prop("+str(mlr)+") <= '1' ;\n")

        #     else:

        #         if (lut_string_value[mlr] == 'E'):
        #             file.write('lut_inst_'+str(mlr)+': lut6_2 \n')
        #             file.write('\n generic map(INIT => X"'+0660066008800880+'") \n')
        #             file.write('port map( \n')
        #             file.write('I0 => a('+str(mlr)+'),  \n')
        #             file.write('I1 => b('+str(mlr)+'),  \n')
        #             file.write('I2 => a('+str(mlr+1)+'),  \n')
        #             file.write('I3 => b('+str(mlr+1)+'),  \n')
        #             file.write("I4 => '0',  \n")
        #             file.write("I5 => '1', \n")
        #             file.write('O5 => gen('+str(mlr)+'), \n')
        #             file.write('O6 => prop('+str(mlr)+') \n')
        #             file.write('); \n')
        #         else:
        #             file.write("gen("+str(mlr)+") <= '0' ;\n")
        #             file.write("prop("+str(mlr)+") <= '1' ;\n")

        # else:

        #     if (lut_string_value[mlr] == 'E'):
        #         file.write('lut_inst_'+str(mlr)+': lut6_2 \n')
        #         file.write('generic map(INIT => X"EEEEEEEE00000000") \n')
        #         file.write('port map( \n')
        #         file.write('I0 => a('+str(mlr)+'),  \n')
        #         file.write('I1 => b('+str(mlr)+'),  \n')
        #         file.write("I2 => '0',  \n")
        #         file.write("I3 => '0',  \n")
        #         file.write("I4 => '0', \n")
        #         file.write("I5 => '1', \n")
        #         file.write('O5 => gen('+str(mlr)+'), \n')
        #         file.write('O6 => prop('+str(mlr)+') \n')
        #         file.write('); \n')
        #     else:
        #         file.write("gen("+str(mlr)+") <= '0' ;\n")
        #         file.write("prop("+str(mlr)+") <= '1' ;\n")


    file.write('prop_gen_assign: \n')
    file.write('if slice_size > word_size generate \n')
    file.write('slice_check: \n')
    file.write('for i in (slice_size-1) to word_size generate \n')
    file.write("gen(i) <= '0'; \n")
    file.write("prop(i) <= '0'; \n")
    file.write(' end generate slice_check; \n')
    file.write('end generate prop_gen_assign; \n')
    file.write('\n')

    file.write('carry_chain: \n')
    file.write('for k in 0 to (slice_size/4 - 1) generate \n')
    file.write('carry_inst0: CARRY4 \n')
    file.write('port map ( \n')
    file.write('DI => gen(k*4+3 downto k*4), \n')
    file.write('S => prop(k*4+3 downto k*4), \n')
    file.write('O => output(k*4+3 downto k*4), \n')
    file.write('CO => carries(k*4+3 downto k*4), \n')
    file.write('CI => input_carry(k), \n')
    file.write("CYINIT => '0' \n")
    file.write('); \n')
    file.write('input_carry(k+1) <= carries(k*4+3); \n')
    file.write('end generate carry_chain; \n')

    for out_assign in range(0, bit_width):
        # file.write('sum('+str(out_assign)+') <= output('+str(out_assign)+');\n')
        if (enabled[out_assign] == 'E'):
            file.write('sum('+str(out_assign)+') <= output('+str(out_assign)+');\n')
        elif (enabled[out_assign] == 'Z'):
            file.write("sum("+str(out_assign)+") <= '0';\n")

        else:
            file.write("sum("+str(out_assign)+") <= '1';\n")
   # file.write('sum(word_size) <= carries(word_size-1); \n')
    file.write('end Behavioral; \n')



    file.close()
    os.chdir(str(called_dir))

def find_input(port, assignments):
    curr_port = assignments[port]
    str_val = ""
    
    if curr_port[0] == 0:
        str_val = str_val + "'" + str(curr_port[1]) + "'"

    elif curr_port[0] == 1:
        str_val = str_val + 'a(' + str(curr_port[1]) + ')'

    elif curr_port[0] == 2:
        str_val = str_val + 'b(' + str(curr_port[1]) + ')'

    return str_val
