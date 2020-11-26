#!/usr/bin/env python

import simpy
from hwsim_utils import *
from base_level import Base_level
from packet import Packet_descriptior

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe

        self.pkt_cnt = 0

        # Peixuan: Base Level

        self.fifo_num = 10

        # number of tesing packets
        self.num_test_pkts = 20

        # create the pipes used for communication with the Base_level object

        # Initialize FIFO array and read/write handle
        
        self.fifo_r_in_pipe_arr = []
        self.fifo_r_out_pipe_arr = []
        self.fifo_w_in_pipe_arr = []
        self.fifo_w_out_pipe_arr = []
        
        index = 0
        while (index < self.fifo_num):
            self.fifo_r_in_pipe_arr.append(simpy.Store(env))
            self.fifo_r_out_pipe_arr.append(simpy.Store(env))
            self.fifo_w_in_pipe_arr.append(simpy.Store(env))
            self.fifo_w_out_pipe_arr.append(simpy.Store(env)) 

            index = index + 1

        # instantiate the Base_Level object

        granularity = 1
        fifo_size = 128

        fifo_write_latency = 1
        fifo_read_latency = 1
        fifo_check_latency = 1
        fifo_num = 10
        initial_vc = 0

        self.blevel = Base_level(env, line_clk_period, sys_clk_period, granularity, fifo_size, self.fifo_r_in_pipe_arr, self.fifo_r_out_pipe_arr, \
        self.fifo_w_in_pipe_arr, self.fifo_w_out_pipe_arr, fifo_write_latency, fifo_read_latency, \
        fifo_check_latency, fifo_num, initial_vc)
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())

        #self.env.process(self.gearbox.migration()) # TODO: fix this

    def sched_enq(self):
        while True:
            (head_seg_ptr, meta_ptr, tuser) = yield self.ptr_out_pipe.get()
            cur_pkt = Packet_descriptior(head_seg_ptr, tuser)
            #print("meta_ptr = {}".format(meta_ptr))   # Peixuan debug
            #print("meta_ptr.rank = {}".format(meta_ptr.rank))   # Peixuan debug
            #print("head_seg_ptr = {}".format(head_seg_ptr))   # Peixuan debug
            #print("cur_pkt = {}".format(cur_pkt))   # Peixuan debug
            #print("cur_pkt address = {}".format(cur_pkt.get_address()))   # Peixuan debug
            #print("cur_pkt Tuser = {}".format(cur_pkt.get_tuser))   # Peixuan debug
            #print("cur_pkt Finish time = {}".format(cur_pkt.tuser.rank))   # Peixuan debug
            self.blevel.enque(cur_pkt)
            print ('@ {} - Enqueue: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))
            self.pkt_cnt = self.pkt_cnt + 1

    def sched_deq(self):
        while True:
            # wait for 10 cycles
            #for j in range(10):
            #    yield self.wait_clock()
            
            #if len(self.pkt_cnt) > 0:
            if self.pkt_cnt > 0:
                pkt_des = self.blevel.deque_earliest_pkt()
                head_seg_ptr = pkt_des.get_address()
                meta_ptr = pkt_des.get_tuser()
                print ('@ {} - Dequeue: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))
                self.pkt_cnt = self.pkt_cnt - 1
                # submit read request
                self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))
