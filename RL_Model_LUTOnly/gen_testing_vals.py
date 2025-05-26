# import numpy as np
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


with open("testing_values.csv","w",newline='') as state_file:
    writer = csv.writer(state_file)

    for t in range(10000):
        x = random.randint(1, 254)
        a = random.randint(0, x)
        b = random.randint(0, 255 - x)

        writer.writerow([str(a)+"  "+str(b)])