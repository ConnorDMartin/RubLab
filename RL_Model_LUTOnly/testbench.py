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

def generate_state():
    state = [[0x6666666688888888, [[0, 1], [0, 0], [2, 1], [1, 1], [2, 0], [1, 0]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 2], [1, 2], [2, 1], [1, 1]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 3], [1, 3], [2, 2], [1, 2]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 4], [1, 4], [2, 3], [1, 3]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 5], [1, 5], [2, 4], [1, 4]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 6], [1, 6], [2, 5], [1, 5]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]], 1]]
    num_disabled = random.randint(1, 3)
    disabled_luts = []
    for i in range(num_disabled):
        dis_ = random.randint(0, 7)
        while dis_ in disabled_luts:
            dis_ = random.randint(0, 7)
        state[dis_][-1] = 0

    return state


print(generate_state())