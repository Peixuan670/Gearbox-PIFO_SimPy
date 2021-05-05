import math
from hwsim_utils import *
from packet import Packet_descriptior
from queues import FIFO, PIFO

# Peixuan 11122020
# This is the base level (level 0), no pifo
class Gearbox_level(HW_sim_object):
    # Public
    def __init__(self, env, line_clk_period, sys_clk_period, granularity, fifo_size, \
                 enq_pipe_cmd, enq_pipe_sts, deq_pipe_req, deq_pipe_dat, \
                 find_earliest_fifo_pipe_req, find_earliest_fifo_pipe_dat, \
                 fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, fifo_w_in_pipe_arr, fifo_w_out_pipe_arr, \
                 level_index, level_set,\
                 fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0):
                 
        super(Gearbox_level, self).__init__(env, line_clk_period, sys_clk_period)
        self.granularity = granularity      # Level Grabularuty, units of VC
        self.fifo_num = fifo_num            # Level fifo num
        self.fifo_size = fifo_size          # Level fifo size, all the fifos in a level has the same size
        self.enq_pipe_cmd = enq_pipe_cmd    # Level enque pipe input 
        self.enq_pipe_sts = enq_pipe_sts    # Level enque pipe output
        self.deq_pipe_req = deq_pipe_req    # Level deque pipe input
        self.deq_pipe_dat = deq_pipe_dat    # Level deque pipe output
        self.find_earliest_fifo_pipe_req = find_earliest_fifo_pipe_req      # depreciated
        self.find_earliest_fifo_pipe_dat = find_earliest_fifo_pipe_dat      # depreciated
        # fifo read/write latency (of each fifo)
        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency    # depreciated

        self.level_index = level_index
        self.level_set = level_set

        self.fifos = []     # fifo array

        # Initialize VC

        self.vc = initial_vc
        self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num  # find current fifo (by VC and granularity)

        # Initialize pkt cnt
        self.pkt_cnt = 0
        
        # Initialize FIFO array and read/write pipe array
        
        self.fifo_r_in_pipe_arr = fifo_r_in_pipe_arr
        self.fifo_r_out_pipe_arr = fifo_r_out_pipe_arr
        self.fifo_w_in_pipe_arr = fifo_w_in_pipe_arr
        self.fifo_w_out_pipe_arr = fifo_w_out_pipe_arr
        
        index = 0
        while (index < self.fifo_num):
            init_items = []
            # creat each fifo and append to fifo array
            new_fifo = FIFO(env, line_clk_period, sys_clk_period, self.fifo_r_in_pipe_arr[index], self.fifo_r_out_pipe_arr[index], \
                self.fifo_w_in_pipe_arr[index], self.fifo_w_out_pipe_arr[index], self.fifo_size, \
                    self.fifo_write_latency, self.fifo_read_latency, init_items)
            self.fifos.append(new_fifo) 

            index = index + 1
            
        self.run()

    def run(self):
        self.env.process(self.enqueue_p())  # enque process
        self.env.process(self.dequeue_p())  # deque process
        self.env.process(self.find_earliest_non_empty_fifo_p()) # depreciated

    # Public
    
    def find_earliest_non_empty_fifo_p(self):   # depreciated        
        while True:
            index = yield self.find_earliest_fifo_pipe_req.get() # fifo index, find the earliest non-empty fifo from this fifo
            print ('[Level {} {}] Check earliest fifo from index {}'.format(self.level_index, self.level_set, index))
            yield self.wait_sys_clks(self.fifo_check_latency) # 02232021 Peixuan: put this delay elsewhere
            non_empty_fifo_index = self.check_non_empty_fifo(index)
            print ('[Level {} {}] Found earliest fifo index = {}'.format(self.level_index, self.level_set, non_empty_fifo_index))
            self.find_earliest_fifo_pipe_dat.put(non_empty_fifo_index)

    def find_earliest_non_empty_fifo(self, index):
        print ('[Level {} {} function] Check earliest fifo from index {}'.format(self.level_index, self.level_set, index))
        non_empty_fifo_index = self.check_non_empty_fifo(index)
        print ('[Level {} {} function] Found earliest fifo index = {}'.format(self.level_index, self.level_set, non_empty_fifo_index))
        return non_empty_fifo_index
    
    def check_non_empty_fifo(self, index):
        cur_index = index
        while cur_index < self.fifo_num:
            if not self.fifos[cur_index].get_len() == 0:
                self.find_earliest_fifo_pipe_dat.put(cur_index)
                print ('[Level {} {}] Found earliest fifo{}'.format(self.level_index, self.level_set, cur_index))
                print ('[Level {} {}] returning fifo{}'.format(self.level_index, self.level_set, cur_index))
                return cur_index
            cur_index = cur_index + 1
        print ('[Level {} {}] All fifos are empty'.format(self.level_index, self.level_set))
        return -1

    
    
    def enqueue_p(self):
        # enqueue process
        # enque includes queue index to enque
        while True:
            (pkt, enque_fifo_index) = yield self.enq_pipe_cmd.get() 
            if not pkt == 0:
                self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
                yield self.fifo_w_out_pipe_arr[enque_fifo_index].get()
                print("[Level {} {}] pkt {} enqued fifo {}".format(self.level_index, self.level_set, pkt.get_uid(), enque_fifo_index))
                self.enq_pipe_sts.put((0, 0))
                self.pkt_cnt = self.pkt_cnt + 1 # update level pkt cnt
            else:
                print("[Level{} {}] Illegal packet".format(self.level_index, self.level_set))

    def dequeue_p(self):
        # dequeue process
        # deque request includes queue index to deque
        while True:
            index = yield self.deq_pipe_req.get()
            if self.deq_pipe_dat is not None:
                self.fifo_r_in_pipe_arr[index].put(1)
                dequed_pkt = yield self.fifo_r_out_pipe_arr[index].get()
                self.deq_pipe_dat.put((dequed_pkt, 0))
                self.pkt_cnt = self.pkt_cnt - 1 # update level pkt cnt


    def update_vc(self, vc):
        # Update vc
        if self.vc < vc:
            self.vc = vc
        # update current serving fifo
        old_fifo = self.cur_fifo
        if self.fifos[self.cur_fifo].get_len() == 0:
            self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num       
        
        is_new_fifo = not (old_fifo==self.cur_fifo)
        return (self.vc, is_new_fifo) # to see if the cur_fifo is updated
    
    def get_vc(self):
        return self.vc
    
    def get_cur_fifo(self):
        return self.fifos[self.cur_fifo]
    
    def get_pkt_cnt(self):
        return self.pkt_cnt