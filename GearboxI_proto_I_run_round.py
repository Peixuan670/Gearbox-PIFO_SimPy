import math
from hwsim_utils import *
from packet import Packet_descriptior
from queues import FIFO, PIFO
from gearbox_level import Gearbox_level

# Peixuan 01142020
# This is Gearbox I
# Prototype I: multi_level, has ping pong, no step down
# NOTICE: This prototype is for functional test: each round round only plus 1
class Gearbox_I(HW_sim_object):
    # Public
    def __init__(self, env, line_clk_period, sys_clk_period, \
        gb_enq_pipe_cmd, gb_enq_pipe_sts, gb_deq_pipe_req, gb_deq_pipe_dat, \
        vc_data_pipe, drop_pipe, \
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
        self.drop_pipe = drop_pipe

        self.vc = initial_vc
        self.pkt_cnt = 0
        self.level_num = 3

        # Initiate all the levels
        #self.levels = []
        # ping pong levels
        self.levelsA = []
        self.levelsB = []

        # fifo function input/output pipes
        self.fifo_r_in_pipe_matrix_A = []       # Two dimentional matrix
        self.fifo_r_out_pipe_matrix_A = []      # Two dimentional matrix
        self.fifo_w_in_pipe_matrix_A = []       # Two dimentional matrix
        self.fifo_w_out_pipe_matrix_A = []      # Two dimentional matrix

        self.fifo_r_in_pipe_matrix_B = []       # Two dimentional matrix
        self.fifo_r_out_pipe_matrix_B = []      # Two dimentional matrix
        self.fifo_w_in_pipe_matrix_B = []       # Two dimentional matrix
        self.fifo_w_out_pipe_matrix_B = []      # Two dimentional matrix

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
                self.enq_pipe_cmd_arr_A[index], self.enq_pipe_sts_arr_A[index], self.deq_pipe_req_arr_A[index], self.deq_pipe_dat_arr_A[index], \
                self.find_earliest_fifo_pipe_req_arr_A[index], self.find_earliest_fifo_pipe_dat_arr_A[index], \
                self.fifo_r_in_pipe_matrix_A[index], self.fifo_r_out_pipe_matrix_A[index], \
                self.fifo_w_in_pipe_matrix_A[index], self.fifo_w_out_pipe_matrix_A[index], \
                fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0)

            self.levelsA.append(cur_level)
            
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
                self.enq_pipe_cmd_arr_B[index], self.enq_pipe_sts_arr_B[index], self.deq_pipe_req_arr_B[index], self.deq_pipe_dat_arr_B[index], \
                self.find_earliest_fifo_pipe_req_arr_B[index], self.find_earliest_fifo_pipe_dat_arr_B[index], \
                self.fifo_r_in_pipe_matrix_B[index], self.fifo_r_out_pipe_matrix_B[index], \
                self.fifo_w_in_pipe_matrix_B[index], self.fifo_w_out_pipe_matrix_B[index], \
                fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0)

            self.levelsB.append(cur_level)
            
            index = index + 1
        
        
        # Tracking last pkt enque level
        self.prev_enq_level_lst = [0] * 4    # We have 4 flows (flow id) in the simulation
        
        # initiate ping-pong

        self.level_ping_pong_arr = []
        index = 0
        while (index < self.level_num):
            self.level_ping_pong_arr[index] = True
        
        # initiate vc
        self.virtrul_clock = initial_vc

        self.run()
    
    def run(self):
        self.env.process(self.enque_p())
        self.env.process(self.deque_p())
        #self.env.process(self.find_earliest_non_empty_fifo_p())
    
    def enque_p(self):
        while True:
            pkt = yield self.gb_enq_pipe_cmd.get() 
            pkt_finish_time = pkt.get_finish_time()
            tuser = pkt.get_tuser()
            flow_id = tuser.pkt_id[0]

            # find the correct level to enque
            insert_level = self.find_insert_level(pkt_finish_time)

            if insert_level == -1:
                self.gb_enq_pipe_sts.put(0) # pkt overflow
                print("enque pkt overflow, exceeds highest level")
                self.drop_pipe.put((pkt.hdr_addr, pkt.meta_addr, pkt.tuser))
                self.gb_enq_pipe_sts.put(False)
            else:
                if insert_level > self.prev_enq_level_lst[flow_id]:
                    self.prev_enq_level_lst[flow_id] = insert_level # update prev_enq_level
                else:
                    insert_level = self.prev_enq_level_lst[flow_id] # if last_enq_level >= insert level, enque last_enq_level

                fifo_index_offset = self.find_enque_index_offset(insert_level, pkt_finish_time)
                current_fifo_index = 0
                if (self.level_ping_pong_arr[insert_level] == True):
                    # Current serving set A
                    current_fifo_index = self.levelsA[insert_level].cur_fifo
                else:
                    # Current serving set B
                    current_fifo_index = self.levelsB[insert_level].cur_fifo
                
                enque_current_set = ((current_fifo_index + fifo_index_offset) < self.fifo_num_list[insert_level])
                #enque_current_set = self.enque_current_set(insert_level, pkt_finish_time)

                if (((self.level_ping_pong_arr[insert_level] == True) and enque_current_set)):
                    # Case 01: Enque current Set A
                    enque_index = current_fifo_index + fifo_index_offset
                    self.enq_pipe_cmd_arr_A[insert_level].put((pkt, enque_index))
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_A[insert_level].get()
                elif (((self.level_ping_pong_arr[insert_level] == False) and enque_current_set)):
                    # Case 02: Enque current Set B
                    enque_index = current_fifo_index + fifo_index_offset
                    self.enq_pipe_cmd_arr_B[insert_level].put((pkt, enque_index))
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_B[insert_level].get()
                elif (((self.level_ping_pong_arr[insert_level] == True) and not enque_current_set)):
                    # Case 02: Enque next Set B
                    enque_index =  fifo_index_offset - current_fifo_index
                    self.enq_pipe_cmd_arr_B[insert_level].put((pkt, enque_index))
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_B[insert_level].get()
                else:
                    # Case 02: Enque next Set A
                    enque_index =  fifo_index_offset - current_fifo_index
                    self.enq_pipe_cmd_arr_A[insert_level].put((pkt, enque_index))
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr_A[insert_level].get()

                self.pkt_cnt = self.pkt_cnt + 1
                self.gb_enq_pipe_sts.put(True) # enque successfully    
    
    def deque_p(self):
        while True:
            yield self.gb_deq_pipe_req.get()

            (dequed_pkt, if_reload) = (0, False)
            deque_level_index = self.find_deque_level()
            while deque_level_index == -1:
                print("Finished serving all levelsm move to next round")
                # TODO Run round until not return -1
                self.run_round()
                deque_level_index = self.find_deque_level()
            if self.level_ping_pong_arr[deque_level_index]:
                # Serve set A in ping-pong fifos
                dequed_fifo = self.levelsA[deque_level_index].cur_fifo
                self.deq_pipe_req_arr_A[deque_level_index].put(dequed_fifo)
                (dequed_pkt, if_reload) = yield self.deq_pipe_dat_arr_A[deque_level_index].get()
            else:
                # Serve set B in ping-pong fifos
                dequed_fifo = self.levelsB[deque_level_index].cur_fifo
                self.deq_pipe_req_arr_B[deque_level_index].put(dequed_fifo)
                (dequed_pkt, if_reload) = yield self.deq_pipe_dat_arr_B[deque_level_index].get()

            # Update served bytes
            self.deque_served_bytes[deque_level_index] = self.deque_served_bytes[deque_level_index] + dequed_pkt.get_bytes() # TODO get pkt len
            self.pkt_cnt = self.pkt_cnt - 1     # update pkt_cnt

            # return pkt
            self.gb_deq_pipe_dat.put((dequed_pkt, 0))
    
    # Private
    '''def run_round(self):
        # get the number of pkt that need to serve in each level
        updated_vc = self.vc + self.granularity_list[0] # move to next vc (based on the finest granularity)

        index = 0
        # Update ping-pong in each level
        while (index < self.level_num):
            serve_set_A = (updated_vc % self.granularity_list[index] == 0)
            self.level_ping_pong_arr[index] = serve_set_A

            # Update vc and cur fifo in each level
            # TODO: doesn't matter if we update both set A and B?
            self.levelsA[index].update_vc(updated_vc)
            self.levelsB[index].update_vc(updated_vc)

            # Update deque_bytes and deque_served_bytes

            self.deque_bytes[index] = 
            self.deque_served_bytes[index] = 0'''
        
        
    
    def find_enque_index_offset(self, level_index, finish_time):
        # We need to find which fifo to enque at Gearbox level
        fifo_index_offset = math.floor(finish_time / self.granularity_list[level_index]) - math.floor(self.vc / self.granularity_list[level_index])
        if fifo_index_offset < 0:
            fifo_index_offset = 0 # if pkt's finish time has passed, enque the current fifo
        # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
        return fifo_index_offset


    '''def enque_current_set(self, level_index, fifo_index_offset):
        if self.level_ping_pong_arr[level_index]:
            # Find max vc of this set
            set_max_vc = (math.floor(self.vc/self.granularity_list[level_index]) + (self.fifo_num_list[level_index] - self.levelsA[level_index].cur_fifo)) * self.granularity_list[level_index]
            if finish_time < set_max_vc: # TODO: < or <=
                return True
            else:
                return False
        else:
            set_max_vc = (math.floor(self.vc/self.granularity_list[level_index]) + (self.fifo_num_list[level_index] - self.levelsB[level_index].cur_fifo)) * self.granularity_list[level_index]
            if finish_time < set_max_vc: # TODO: < or <=
                return True
            else:
                return False'''    
    
    
    def find_deque_level(self):
        index = 0
        while (index < self.level_num):
                if self.deque_bytes[index] > self.deque_served_bytes[index]:
                    return index
        return -1 # If all level has been served, return -1
    
    def run_round(self):
        # We need to update self.level_ping_pong_arr if we finish serving one set
        updated_vc = self.vc + 1
        self.vc = updated_vc

        # Update ping-pong
        index = 0
        while (index < self.level_num):
            serve_set_A = (updated_vc % self.granularity_list[index] == 0)
            self.level_ping_pong_arr[index] = serve_set_A

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

            # TODO: Not sure
            if (is_new_fifo):
                deque_byte = (self.granularity_list[0]/self.granularity_list[index]) * cur_fifo.get_bytes() # TODO we need to implement get_bytes() function in FIFO
                self.deque_bytes[index] = deque_byte
                #self.deque_served_bytes[index] = 0
                #self.deque_flags[index] = True
            self.deque_served_bytes[index] = 0
        
        # Update vc to outside
        self.vc_data_pipe.put(self.vc)
    
    #def update_vc(self, vc):

    def find_insert_level(self, finish_time):
        # insert_level: the insert level of last packet in the flow
        # find the correct level to enque
        index = 0
        while (index < self.level_num):
            level_max_vc = (math.floor(self.vc/self.granularity_list[index]) + self.fifo_num_list[index]) * self.granularity_list[index]

            if finish_time < level_max_vc:
                return index
            index = index + 1
        return -1 # pkt overflow
    
    def get_pkt_cnt(self):
        return self.pkt_cnt
    