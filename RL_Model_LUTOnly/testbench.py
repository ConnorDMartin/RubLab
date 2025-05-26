import numpy as np
# import tensorflow as tf
import random
# from collections import deque
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, Flatten, Input
# from tensorflow.keras.optimizers import Adam
# import subprocess
import csv
import re
# import matplotlib.pyplot as plt

# determine action masking based on values of input state
def get_action_mask(state):
    inter_state = state.reshape(8, 77)
    lut_mask = np.ones((8), dtype=np.float32)
    init_mask = np.ones((64), dtype=np.float32)
    state_tracker = [[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]
    
    for i_ in range(0,8):
        if inter_state[i_][-1] == 0:
            lut_mask[i_] = 0
        else:
            lut = inter_state[i_]
            indx = 0
            while (indx < 6):
                channel = lut[64 + 2*indx]
                selection = lut[64 + 2*indx + 1]
                if (i_ == 0):
                    state_tracker[indx][1] = channel
                    state_tracker[indx][2] = selection
                else:
                    if state_tracker[indx][1] != channel:
                        state_tracker[indx][0] = 0
                    elif (state_tracker[indx][1] == 0) and (state_tracker[indx][2] != selection):
                        state_tracker[indx][0] = 0

                indx+=1

    i_ = 0
    while (i_ < 6):
        if i_ == 0:
            if (state_tracker[0] == 1 ) and (state_tracker[1] == 0):
                if (state_tracker[2] == 0):
                    init_mask[31:63] = [0] * (63-31)

        else:
            if (state_tracker[0] == 1) and (state_tracker[1] == 0):
                iter_ = 0
                while iter_  < 64:
                    if state_tracker[2] == 1:
                        iter_ += (2**(5 - i_))

                    for n_ in range(2**(5 - i_)):
                        init_mask[iter_ + n_] = 0
                    
                    iter_ += 2 * (2**(5 - i_))
        i_+=1

    return lut_mask, init_mask
        
        


def mask_logits(logits, lut_mask, bit_mask):
    lut_logits, bit_logits = logits # (1, 8), (1, 64)

    masked_lut_logits = np.where(lut_mask == 1.0, lut_logits, -1e9)
    masked_bit_logits = np.where(bit_mask == 1.0, bit_logits, -1e9)

    return masked_lut_logits, masked_bit_logits


## Main training loop
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



input_state = [[0x6666666688888888, [[0, 1], [0, 0], [2, 1], [1, 1], [2, 0], [1, 0]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 2], [1, 2], [2, 1], [1, 1]], 0], [0x6666666688888888, [[0, 1], [0, 0], [2, 3], [1, 3], [2, 2], [1, 2]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 4], [1, 4], [2, 3], [1, 3]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 5], [1, 5], [2, 4], [1, 4]], 0], [0x6666666688888888, [[0, 1], [0, 0], [2, 6], [1, 6], [2, 5], [1, 5]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]], 1]]

preprocessed_state = preprocess_state(input_state)
print(get_action_mask(preprocessed_state))