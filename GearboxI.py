import math
from hwsim_utils import *
from packet import Packet_descriptior
from queues import FIFO, PIFO
from gearbox_level import Gearbox_level

# Peixuan 12232020
# This is Gearbox I
class Gearbox_I(HW_sim_object):
    # Public
    def __init__(self, env, line_clk_period, sys_clk_period, \
        gb_enq_pipe_cmd, gb_enq_pipe_sts, gb_deq_pipe_req, gb_deq_pipe_dat, \
        vc_data_pipe,
        granularity_list, fifo_num_list, fifo_size_list, \
        fifo_check_latency=1, initial_vc=0):

        self.granularity_list = granularity_list
        self.fifo_num_list = fifo_num_list
        self.fifo_size_list = fifo_size_list
        self.fifo_check_latency = fifo_check_latency

        # Gearbox enque/deque pipes
        self.gb_enq_pipe_cmd = gb_enq_pipe_cmd
        self.gb_enq_pipe_sts = gb_enq_pipe_sts
        self.gb_deq_pipe_req = gb_deq_pipe_req
        self.gb_deq_pipe_dat = gb_deq_pipe_dat

        self.vc_data_pipe = vc_data_pipe

        # Initiate all the levels
        #self.levels = []
        # ping pong levels
        self.levelsA = []
        self.levelsB = []

        self.fifo_r_in_pipe_matrix_A = [][]
        self.fifo_r_out_pipe_matrix_A = [][]
        self.fifo_w_in_pipe_matrix_A = [][]
        self.fifo_w_out_pipe_matrix_A = [][]

        self.fifo_r_in_pipe_matrix_B = [][]
        self.fifo_r_out_pipe_matrix_B = [][]
        self.fifo_w_in_pipe_matrix_B = [][]
        self.fifo_w_out_pipe_matrix_B = [][]

        # level function input/output pipes
        self.enq_pipe_cmd_arr_A = [] 
        self.enq_pipe_sts_arr_A = []
        self.deq_pipe_req_arr_A = []
        self.deq_pipe_dat_arr_A = []
        self.find_earliest_fifo_pipe_req_arr_A = [] 
        self.find_earliest_fifo_pipe_dat_arr_A = []

        self.enq_pipe_cmd_arr_B = [] 
        self.enq_pipe_sts_arr_B = []
        self.deq_pipe_req_arr_B = []
        self.deq_pipe_dat_arr_B = []
        self.find_earliest_fifo_pipe_req_arr_B = [] 
        self.find_earliest_fifo_pipe_dat_arr_B = []

        # flags & bytes for deque
        #self.deque_flags = []        
        self.deque_bytes = []
        self.deque_served_bytes = []

        index = 0
        while (index < self.level_num):
            #self.deque_flags.append(False)
            self.deque_bytes.append(0)
            self.deque_served_bytes.append(0)


        # initiate levels for set A
        
        index = 0
        while (index < self.level_num):

            fifo_r_in_pipe_arr = []
            fifo_r_out_pipe_arr = []
            fifo_w_in_pipe_arr = []
            fifo_w_out_pipe_arr = []

            while (index < self.fifo_num_list[index]):
                fifo_r_in_pipe_arr.append(simpy.Store(env))
                fifo_r_out_pipe_arr.append(simpy.Store(env))
                fifo_w_in_pipe_arr.append(simpy.Store(env))
                fifo_w_out_pipe_arr.append(simpy.Store(env))

            self.fifo_r_in_pipe_matrix_A.append(fifo_r_in_pipe_arr)
            self.fifo_r_out_pipe_matrix_A.append(fifo_r_out_pipe_arr)
            self.fifo_w_in_pipe_matrix_A.append(fifo_w_in_pipe_arr)
            self.fifo_w_out_pipe_matrix_A.append(fifo_w_out_pipe_arr)

            enq_pipe_cmd = simpy.Store(env)
            enq_pipe_sts = simpy.Store(env)
            deq_pipe_req = simpy.Store(env)
            deq_pipe_dat = simpy.Store(env)
            find_earliest_fifo_pipe_req = simpy.Store(env)
            find_earliest_fifo_pipe_dat = simpy.Store(env)

            self.enq_pipe_cmd_arr_A.append(enq_pipe_cmd)
            self.enq_pipe_sts_arr_A.append(enq_pipe_sts)
            self.deq_pipe_req_arr_A.append(deq_pipe_req)
            self.deq_pipe_dat_arr_A.append(deq_pipe_dat)
            self.find_earliest_fifo_pipe_req_arr_A.append(find_earliest_fifo_pipe_req)
            self.find_earliest_fifo_pipe_dat_arr_A.append(find_earliest_fifo_pipe_dat)

            cur_level = Gearbox_level(env, line_clk_period, sys_clk_period, self.granularity_list[index], self.fifo_size_list[index], \
                self.enq_pipe_cmd_arr[index], self.enq_pipe_sts_arr[index], self.deq_pipe_req_arr[index], self.deq_pipe_dat_arr[index], \
                self.find_earliest_fifo_pipe_req_arr[index], self.find_earliest_fifo_pipe_dat_arr[index], \
                self.fifo_r_in_pipe_matrix[index], self.fifo_r_out_pipe_matrix[index], \
                self.fifo_w_in_pipe_matrix[index], self.fifo_w_out_pipe_matrix[index], \
                fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0):

            self.levels_A.append(cur_level)
            
            index = index + 1
        
        # initiate levels for set B
        
        index = 0
        while (index < self.level_num - 1): # Highest level doesn't need ping-pong

            fifo_r_in_pipe_arr = []
            fifo_r_out_pipe_arr = []
            fifo_w_in_pipe_arr = []
            fifo_w_out_pipe_arr = []

            while (index < self.fifo_num_list[index]):
                fifo_r_in_pipe_arr.append(simpy.Store(env))
                fifo_r_out_pipe_arr.append(simpy.Store(env))
                fifo_w_in_pipe_arr.append(simpy.Store(env))
                fifo_w_out_pipe_arr.append(simpy.Store(env))

            self.fifo_r_in_pipe_matrix_B.append(fifo_r_in_pipe_arr)
            self.fifo_r_out_pipe_matrix_B.append(fifo_r_out_pipe_arr)
            self.fifo_w_in_pipe_matrix_B.append(fifo_w_in_pipe_arr)
            self.fifo_w_out_pipe_matrix_B.append(fifo_w_out_pipe_arr)

            enq_pipe_cmd = simpy.Store(env)
            enq_pipe_sts = simpy.Store(env)
            deq_pipe_req = simpy.Store(env)
            deq_pipe_dat = simpy.Store(env)
            find_earliest_fifo_pipe_req = simpy.Store(env)
            find_earliest_fifo_pipe_dat = simpy.Store(env)

            self.enq_pipe_cmd_arr_B.append(enq_pipe_cmd)
            self.enq_pipe_sts_arr_B.append(enq_pipe_sts)
            self.deq_pipe_req_arr_B.append(deq_pipe_req)
            self.deq_pipe_dat_arr_B.append(deq_pipe_dat)
            self.find_earliest_fifo_pipe_req_arr_B.append(find_earliest_fifo_pipe_req)
            self.find_earliest_fifo_pipe_dat_arr_B.append(find_earliest_fifo_pipe_dat)

            cur_level = Gearbox_level(env, line_clk_period, sys_clk_period, self.granularity_list[index], self.fifo_size_list[index], \
                self.enq_pipe_cmd_arr[index], self.enq_pipe_sts_arr[index], self.deq_pipe_req_arr[index], self.deq_pipe_dat_arr[index], \
                self.find_earliest_fifo_pipe_req_arr[index], self.find_earliest_fifo_pipe_dat_arr[index], \
                self.fifo_r_in_pipe_matrix[index], self.fifo_r_out_pipe_matrix[index], \
                self.fifo_w_in_pipe_matrix[index], self.fifo_w_out_pipe_matrix[index], \
                fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0):

            self.levels_B.append(cur_level)
            
            index = index + 1
        
        
        # initiate ping-pong

        self.level_ping_pong_arr = []
        index = 0
        while (index < self.level_num):
            self.level_ping_pong_arr[index] = True
        
        # initiate vc
        self.virtrul_clock = initial_vc

        self.run()
    
    def run(self):
        self.env.process(self.enqueue_p())
        self.env.process(self.dequeue_p())
        #self.env.process(self.find_earliest_non_empty_fifo_p())
    
    def enque_p(self):
        while True:
            pkt = yield self.gb_enq_pipe_cmd.get() 
            pkt_finish_time = pkt.get_finish_time()

            # find the correct level to enque
            insert_level = self.find_insert_level(pkt_finish_time)

            if insert_level = -1:
                self.gb_enq_pipe_sts.put(0) # pkt overflow
            else:

                #insert_level = max(insert_level, last_pkt_level)

                if (self.level_ping_pong_arr[index] == True):
                    self.enq_pipe_cmd_arr_A[index].put(pkt_des)
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_A[index].get()               
                else:
                    self.enq_pipe_cmd_arr_B[index].put(pkt_des)
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_B[index].get()  

                self.gb_enq_pipe_sts.put(1) # enque successfully
    
    
    def deque_p(self):
        while True:
            yield self.gb_deq_pipe_req.get()
            
            index = 0
            while (index < self.level_num):
                if self.deque_bytes[index] > self.deque_served_bytes[index]:
                    if self.level_ping_pong_arr[index]:
                        dequed_fifo = self.levelsA[index].cur_fifo
                        self.deq_pipe_req_arr_A[index].put(dequed_fifo)
                        (dequed_pkt, if_reload) = yield self.deq_pipe_dat_arr_A[index].get()
                    else:
                        dequed_fifo = self.levelsB[index].cur_fifo
                        self.deq_pipe_req_arr_B[index].put(dequed_fifo)
                        (dequed_pkt, if_reload) = yield self.deq_pipe_dat_arr_B[index].get()
                        
                    # we need to get the byte of this pkt
                    self.deque_served_bytes[index] = self.deque_served_bytes[index] + dequed_pkt.get_len() # TODO get pkt len
                    break # TODO break to where

            
        # check if each level have pkt to serve
        # if not: run round
        # serve level
    
    # Private
    #def run_round(self):
        # get the number of pkt that need to serve in each level
    
    def update_vc(self, vc):
        # We need to update self.level_ping_pong_arr if we finish serving one set
        self.vc = self.vc + 1

        # for each level to find current serving fifos
        index = 0
        while (index < self.level_num):
            # TODO: not sure how to handle ping-pong levels
            is_new_fifo_A = self.levelsA[index].update_vc(self.vc)[1] # update_vc will return (vc, is_updated)
            is_new_fifo_B = self.levelsB[index].update_vc(self.vc)[1]

            is_new_fifo = False

            if (self.level_ping_pong_arr[index] == True):
                cur_fifo = self.levelsA[index].get_cur_fifo()
                is_new_fifo = is_new_fifo_A
            else:
                cur_fifo = self.levelsB[index].get_cur_fifo()
                is_new_fifo = is_new_fifo_B

            if (is_new_fifo):
                deque_byte = (self.granularity_list[0]/self.granularity_list[index]) * cur_fifo.get_bytes() # TODO we need to implement get_bytes() function in FIFO
                self.deque_bytes[index] = deque_byte
                self.deque_served_bytes[index] = 0
                #self.deque_flags[index] = True
        
        self.vc_data_pipe.put(self.vc)


    def find_insert_level(self, finish_time):
        # insert_level: the insert level of last packet in the flow
        # find the correct level to enque
        index = 0
        while (index < self.level_num):
            level_max_vc = math.floor(self.vc/self.granularity_list[index]) + self.granularity_list[index] * self.fifo_num_list[index]

            if pkt_finish_time < level_max_vc:
                return index
            index = index + 1
        return -1 # pkt overflow
    