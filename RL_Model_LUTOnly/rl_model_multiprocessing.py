## Import required libraries
import numpy as np
import tensorflow as tf
import random
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Input
from tensorflow.keras.optimizers import Adam
import subprocess
from pathlib import Path
import csv
import matplotlib.pyplot as plt
import copy
import os
from behavioral.calculate_error import get_error
import re

## Build the environment
class Env:
    def __init__(self, input_state):
        self.state = copy.deepcopy(input_state)
        self.init_state = copy.deepcopy(input_state)
        self.initial_error = 0

        # print("Intput to ENV INIT: "+str(input_state)+"\n") ## debugging print ##

        # print("Active LUTs: "+str(self.active)+"\n") ## debugging print ##
        self.num_luts = 8
        self.lut_size = 64
        self.num_inputs = 12

        self.run_iter = 0

        # save current state to a file for access in top_lut_new.py
        with open("current_state.csv","w",newline='') as state_file:
            writer = csv.writer(state_file)
            writer.writerows(self.state)
            writer.writerow([self.run_iter])

        ## Delete after debug ##
        with open("current_state.csv","r") as state_file:
            data_list = []
            reader = csv.reader(state_file)
            for row in reader:
                int_row = [int(item) for item in row]
                data_list.append(int_row)
            last_row = data_list[-1]
            data_list.pop(-1)

        # Get Initial Error

        # result_ = subprocess.run(["bash", "main.sh"], cwd=script_dir, check=True)
        # result_ = subprocess.run(["bash", "main.sh"])

        # filename = './results/summary/results_combined_4.csv'

        # with open(filename, 'r', newline='') as file:
        #     reader = list(csv.reader(file))
        #     last_row = reader[-1]
        #     avg_error = float(last_row[-7])
        print("Getting Initial Error")
        avg_error = get_error(self.state, testing_data)
        print("Initial Error: "+str(avg_error))
        
        self.initial_error = avg_error
    
    def reset(self, episodes_elapsed, state_num):
        if episodes_elapsed == 25:
            inter_state = generate_state(state_num)
            inter_state = preprocess_state(inter_state)
            self.state = copy.deepcopy(inter_state)

            print("Getting Initial Error")
            avg_error = get_error(self.state, testing_data)
            print("Initial Error: "+str(avg_error))
            self.initial_error = avg_error
        else:
            self.state = copy.deepcopy(self.init_state)
        return self.state
    
    def step(self, action):

        lut_choice = action[0]
        bit_choice = action[1]

        self.state = self.state.reshape(8, 77)
        self.state[lut_choice][bit_choice] = 1 - self.state[lut_choice][bit_choice]

        print(self.state)
            

        # save current state to a file for access in top_lut_new.py
        with open("current_state.csv","w",newline='') as state_file:
            writer = csv.writer(state_file)
            writer.writerows(self.state)
            writer.writerow([self.run_iter])

        ## reward function
        # subprocess.run(["bash", "main.sh"])

        # filename = './results/summary/results_combined_4.csv'

        # with open(filename, 'r', newline='') as file:
        #     reader = list(csv.reader(file))
        #     last_row = reader[-1]
        #     avg_error = float(last_row[-7])

        print("Getting Error")
        avg_error = get_error(self.state, testing_data)
        print("Error: "+str(avg_error))


        reward = (abs(self.initial_error) - abs(avg_error)) # Reward from current state
        done = 1 if (abs(avg_error) < (0.2 * self.initial_error)) else 0 # Episode ends if target is reached

        if reward < 0:
            reward = reward/10

        return np.array(self.state).flatten(), reward, done, avg_error

## Build the DGN agent

class Agent:
    def __init__(self, input_state):
        ## hyperparameters
        self.active = 0
        # determine size of active part of lUT
        lut_indx = 0
        self.lut_num = 8
        for lut_ in input_state:
            if lut_[0] != empty_compressed_lut[0]:
                self.active = lut_indx + 1
            lut_indx += 1
        
        self.state_size = (self.lut_num, (77))
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95 #discount factor
        self.epsilon = 1.0 #exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.01
        self.batch_size = 4

        self.model = self.build_model()
        self.lut_mask, self.bit_mask = self.get_action_mask(input_state)

    def build_model(self):


        input = tf.keras.layers.Input(shape=self.state_size, name = "state")
        flat = tf.keras.layers.Flatten()(input)
        x = tf.keras.layers.Dense(1024, activation="relu")(flat)
        x = tf.keras.layers.Dense(512, activation="relu")(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)


        lut_head = tf.keras.layers.Dense(8, name = "lut")(x)
        bit_head = tf.keras.layers.Dense(64, name = "bit")(x)

        model = tf.keras.Model(inputs = input, outputs = [lut_head, bit_head])

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), loss=["mse", "mse"])

        
        # return model
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        # if np.random.rand() <= self.epsilon:
        #     return [random.randint(0, 8 - 1), random.randint(0, 64 - 1)] #random action (exploration)
        # else:
        #     q_values = self.model.predict(state.reshape(1, 8, 77), verbose=0)
        #     return [np.argmax(ind_q_values[0]) for ind_q_values in q_values] #best action (exploitation)
        
        if np.random.rand() <= self.epsilon:
            valid_idx_lut = np.argwhere(self.lut_mask == 1)
            valid_idx_bit = np.argwhere(self.bit_mask == 1)
            
            selected_lut = valid_idx_lut[random.randint(0, len(valid_idx_lut) - 1)]
            selected_bit = valid_idx_bit[random.randint(0, len(valid_idx_bit) - 1)]

            return [int(selected_lut), int(selected_bit)]
        else:
            q_values = self.model.predict(state.reshape(1, 8, 77), verbose=0)
            masked_q_values_lut, masked_q_values_bit = self.mask_logits(q_values, self.lut_mask, self.bit_mask)
            lut_idx = int(np.argmax(masked_q_values_lut))
            bit_idx = int(np.argmax(masked_q_values_bit))

            return [lut_idx, bit_idx]
    
    def train(self):
        if len(self.memory) < self.batch_size:
            return


        # iterate through memory and get rewards
        for state, action, reward, next_state, done in list(self.memory)[-5:]:
            # assign blame to blame mask for rewards
            blame = [1, 1]

            # action_choice = action[6]

            # match action_choice:
            #     case 0:
            #         blame[2] = 1
            #     case 1:
            #         blame[1] = blame[3] = blame[4] = 1
            #     case 2:
            #         blame[1] = blame[5] = 1
        

            next_qs = self.model.predict(next_state.reshape(1, 8, 77), verbose=0)
            target_qs = self.model.predict(state.reshape(1, 8, 77), verbose=0)
            # print(target_qs)

            for head_indx in range(2):

                if blame[head_indx]:
                    target = reward

                    if not done:
                        target += self.gamma * np.max(next_qs[head_indx][0])

                    target_qs[head_indx][0][action[head_indx]] = target

            self.model.fit(state.reshape(1, 8, 77), target_qs, epochs=1, verbose=0)

        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    
    def log_memory(self, state, error, episode, step, reward):
        state = state.reshape(8, 77)

        filename = './results/summary/run_summary.csv'
        with open(filename,"a") as summary_file:
            summary_file.write("Episode "+str(episode)+" Step "+str(step)+":\n")
            # print(state)
            # summary_file.write(state)
            # for lut in state:
            #     summary_file.write(hex(lut))
            #     summary_file.write(', ')
    
            for s_ in state:
                # convert binary value of LUT init code to hex
                init_code = 0
                for t_ in range(64):
                    init_code += s_[t_] << (63 - t_)
                summary_file.write(hex(init_code))
                summary_file.write(', ')



            summary_file.write('\n')
            summary_file.write("Error: "+str(error)+"\n")
            summary_file.write("Reward: "+str(reward)+"\n")
            summary_file.write("Exploration Rate: "+str(self.epsilon)+"\n")
            summary_file.write("Enabled: "+str(debugging_list)+"\n")
            summary_file.write("\n")



        return
    

    # determine action masking based on values of input state
    def get_action_mask(self, state):
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
                        if (state_tracker[indx][1] != channel) and (inter_state[i_][-1] != 0):
                            state_tracker[indx][0] = 0
                        elif (state_tracker[indx][1] == 0) and (state_tracker[indx][2] != selection) and (inter_state[i_][-1] != 0):
                            state_tracker[indx][0] = 0
                        elif (channel == 1) or (channel == 2):
                            state_tracker[indx][0] = 0

                    indx+=1

        print("state tracker: " + str(state_tracker))
        i_ = 0
        while (i_ < 6):
            if i_ == 0:
                if (state_tracker[i_][0] == 1 ) and (state_tracker[i_][1] == 0):
                    if (state_tracker[i_][2] == 0):
                        # print("Changing Mask 1")
                        init_mask[31:63] = [0] * (63-31)

            else:
                if (state_tracker[i_][0] == 1) and (state_tracker[i_][1] == 0):
                    # print("Changing Mask 2")
                    iter_ = 0
                    while iter_  < 64:
                        if state_tracker[i_][2] == 1:
                            iter_ += (2**(5 - i_))

                        for n_ in range(2**(5 - i_)):
                            init_mask[iter_ + n_] = 0
                        
                        iter_ += 2 * (2**(5 - i_))
            i_+=1

        return lut_mask, init_mask
            
        

    def mask_logits(self, logits, lut_mask, bit_mask):
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

# Display data after completion
def display_data(LUT_size):
    filename = './results/summary/results_combined_4.csv'

    with open(filename, 'r', newline='') as file:
        reader = list(csv.reader(file))
        last_row = reader[-1]
        CPD = last_row[6]
        Power = last_row[13]
        Active_LUTs = float(last_row[9])
        abs_error = last_row[19]
    PDP = float(CPD) * float(Power)
    PPA = PDP * Active_LUTs
    print("Point Extracted From Results\n")

    # plt.scatter(PPA, abs_error, color='green')

    point_list = []
    print("Comparing LUT Size\n")
    if (LUT_size == 8) or (LUT_size == 7) or (LUT_size == 6):
        if LUT_size == 8:
            print("LUT Size 8\n")
            with open('SignedAdd_8x8_8_AXO_METRICS.csv', 'r', newline='') as file:
                reader = list(csv.reader(file))
                i = 0
                for row in reader:
                    if i != 0:
                        abs_error_d = float(row[19])
                        active_luts_d = float(row[9])

                        CPD_d = float(row[6])
                        Power_d = float(row[13])
                        PDP_d = CPD_d * Power_d
                        PPA_d = PDP_d * active_luts_d

                        point_list.append((abs_error_d, PPA_d))
                        plt.scatter(PPA_d, abs_error_d, color='black')
                    else:
                        i+=1


        elif LUT_size == 7:
            print("LUT Size 7\n")            
            with open('SignedAdd_7x7_7_AXO_METRICS', 'r', newline='') as file:
                reader = list(csv.reader(file))
                i = 0
                for row in reader:
                    if i != 0:
                        abs_error_d = float(row[19])
                        active_luts_d = float(row[9])

                        CPD_d = float(row[6])
                        Power_d = float(row[13])
                        PDP_d = CPD_d * Power_d
                        PPA_d = PDP_d * active_luts_d

                        point_list.append((abs_error_d, PPA_d))
                        plt.scatter(PPA_d, abs_error_d, color='black')
                    else:
                        i+=1

        elif LUT_size == 6:
            print("LUT Size 6\n")
            with open('SignedAdd_6x6_6_AXO_METRICS', 'r', newline='') as file:
                reader = list(csv.reader(file))
                i = 0
                for row in reader:
                    if i != 0:
                        abs_error_d = float(row[19])
                        active_luts_d = float(row[9])

                        CPD_d = float(row[6])
                        Power_d = float(row[13])
                        PDP_d = CPD_d * Power_d
                        PPA_d = PDP_d * active_luts_d

                        point_list.append((abs_error_d, PPA_d))
                        plt.scatter(PPA_d, abs_error_d, color='black')
                    else:
                        i+=1
        print("Comparing Points\n")
        dominated_point = False

        for x,y in point_list:
            x = float(x)
            y = float(y)
            abs_error = float(abs_error)
            if (x <= abs_error) and (y <= PPA):
                if (x < abs_error) or (y < PPA):
                    dominated_point = True
                    break

        if dominated_point == True:
            print("New LUT Config is dominated\n")
        else:
            print("New LUT Config is non-dominated\n")
    else:
        print("No previous data to compare w/ new design\n")

    plt.scatter(abs_error, PPA, color='green')
    plt.xlabel("Absolute Error")
    plt.ylabel("PPA")
    plt.show()

def generate_state(state_num):
    state = [[0x6666666688888888, [[0, 1], [0, 0], [2, 1], [1, 1], [2, 0], [1, 0]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 2], [1, 2], [2, 1], [1, 1]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 3], [1, 3], [2, 2], [1, 2]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 4], [1, 4], [2, 3], [1, 3]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 5], [1, 5], [2, 4], [1, 4]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 6], [1, 6], [2, 5], [1, 5]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]], 1]]
    # num_disabled = random.randint(1, 3)
    # disabled_luts = []
    # for i in range(num_disabled):
    #     dis_ = random.randint(0, 7)
    #     while dis_ in disabled_luts:
    #         dis_ = random.randint(0, 7)
    #     state[dis_][-1] = 0
    
    match state_num:
        case state_num if 0 <= state_num < 8:
            num_disabled = 1
            state[state_num][-1] = 0

        case state_num if 8 <= state_num < 36:
            num_disabled = 2
            disabled_luts = []
            for i in range(num_disabled):
                dis_ = random.randint(0, 7)
                while dis_ in disabled_luts:
                    dis_ = random.randint(0, 7)
                state[dis_][-1] = 0


        case state_num if 36 <= state_num < 92:
            num_disabled = 3
            disabled_luts = []
            for i in range(num_disabled):
                dis_ = random.randint(0, 7)
                while dis_ in disabled_luts:
                    dis_ = random.randint(0, 7)
                state[dis_][-1] = 0


    return state



if __name__ == "__main__" or os.getenv("ALLOW_MULTIPROC") == "1":
    empty_lut = [0x0000000000000000, [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]], 0]
    empty_compressed_lut = preprocess_state([empty_lut])[0]
    # print("Empty compressed lut: "+str(empty_compressed_lut)+"\n") ## debugging print ##

    #for debugging:
    # input_state = [[0x6666666688888888, [[0, 1], [0, 0], [2, 1], [1, 1], [2, 0], [1, 0]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 2], [1, 2], [2, 1], [1, 1]], 0], [0x6666666688888888, [[0, 1], [0, 0], [2, 3], [1, 3], [2, 2], [1, 2]], 1], [0x6666666688888888, [[0, 1], [0, 0], [2, 4], [1, 4], [2, 3], [1, 3]], 1], [0x0000000000000000, [[0, 1], [0, 0], [2, 5], [1, 5], [2, 4], [1, 4]], 0], [0x6666666688888888, [[0, 1], [0, 0], [2, 6], [1, 6], [2, 5], [1, 5]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 6], [1, 6]], 1], [0x6666666688888888, [[0, 1], [0, 0], [0, 0], [0, 0], [2, 7], [1, 7]], 1]]
    state_num = 0
    input_state = generate_state(state_num)
    state_num += 1

    #end debugging
    print("Collecting Testing Data\n")

    testing_data = []
    # Collect Testing data
    with open("testing_values.csv","r",newline='') as state_file:
    # with open("testing_values.csv","r",newline='') as state_file:
        reader = csv.reader(state_file)
        pattern = r"[0-9]+"

        for row in reader:
            arg1, arg2 = re.findall(pattern, str(row))
            testing_data.append([arg1, arg2])

    print("Flag 1\n") ## Debugging Flag ##

    file_path = './results/summary/run_summary.csv'
    if os.path.exists(file_path):
        open(file_path, 'w').close()

    input_state = preprocess_state(input_state)
    print("Flag 2\n") ## Debugging Flag ##
    env = Env(input_state)
    num_of_luts = 8 # Hardcoded for current scope of project
    print("Flag 3\n") ## Debugging Flag ##
    agent = Agent(input_state)

    episodes = 2000  ## SWITCH TO 1000 WHEN NOT DEBUGGING ##
    episodes_elapsed = 0
    # episodes = 1 # for debugging

    print("Flag 4\n") ## Debugging Flag ##
    for episode in range(episodes):
        state = env.reset(episodes_elapsed, state_num)
        if (episodes_elapsed == 25):
            Agent.lut_mask, Agent.bit_mask = Agent.get_action_mask(Agent, state)

            episodes_elapsed = 0

            state_num += 1
            if state_num == 92:
                state_num = 0

        total_reward = 0
        done = 0

        debugging_list = []
        for i in range(8):
            debugging_list.append(state[i][-1])

        print("Flag 5\n") ## Debugging Flag ##
        for step in range(100):   # Done state is either n steps or done is triggered
            action = agent.act(state)
            next_state, reward, done, error = env.step(action) ## Disabled for Debugging ##

            agent.remember(state, action, reward, next_state, done)
            agent.train()  ## Disabled for Debugging ##

            agent.log_memory(state, error, episode, step, reward)

            state = next_state
            total_reward += reward

            if done:
                break
        print("Flag 6\n") ## Debugging Flag ##
        print(f"Episode {episode+1}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.4f}")

        episodes_elapsed += 1


    ## Save model

    agent.model.save("dqn_model.keras")
    print("Training complete, model saved.")

    display_data(num_of_luts)



'''
NOTES
To Do:
- Modify main.sh such that inputs can be modified and LUTs can be enabled/disabled
- Continue to debug existing code
- Ensure Model's logic is sound throughout the training process
- Design done condition for hybrid done episode end condition
- Review reset function in Env, setting to random values may not be best practice
- Rethink how step function works for input port assignments, current implementation not efficient
- Explore further if input masking would help for this application?
- Implement an RNN
- Look into new model inputs and outputs handeling
- implmement action masking
- go through main.sh, verify results csv location/naming
- PPA score is being calculated wrong
- Consider adding another layer between backbone and head for each head
- Use of top_tb.vhd may be wrong
- Reshapes are wrong

- Areas to improve:
- - Add layers to heads
- - Add action masking
- - Refine testing dataset

Original Function Notes:
- main.sh is called to run Vivado code
- - Then calls top_lut_new.py
- - - top_lut_new.py creates list of testConfigs (configs that tell the VHDL enabled state of LUTs and are used for result addressing)
- - - top_lut_new.py then creates the LUTs in VHDL and stores them in results file
- - main_tcl.tcl then iterates through list of testconfigs to run in Vivado

Function notes:
- LUT code binary representation is msb first (at index 0)

Meet with professor tuesday may 6th
'''