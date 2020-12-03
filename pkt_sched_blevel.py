#!/usr/bin/env python

import simpy
from hwsim_utils import *
from base_level import Base_level
from packet import Packet_descriptior
from queues import *

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe

        # blevel
        self.enq_pipe_cmd = simpy.Store(env)
        self.enq_pipe_sts = simpy.Store(env)
        self.deq_pipe_req = simpy.Store(env)
        self.deq_pipe_dat = simpy.Store(env)
        self.find_earliest_fifo_pipe_req = simpy.Store(env)
        self.find_earliest_fifo_pipe_dat = simpy.Store(env)
        #self.fifo_num = fifo_num
        fifo_num = 10

        # Initialize FIFO array and read/write handle
        
        self.fifo_r_in_pipe_arr = []
        self.fifo_r_out_pipe_arr = []
        self.fifo_w_in_pipe_arr = []
        self.fifo_w_out_pipe_arr = []

        index = 0
        while (index < fifo_num):
            self.fifo_r_in_pipe_arr.append(simpy.Store(env))
            self.fifo_r_out_pipe_arr.append(simpy.Store(env))
            self.fifo_w_in_pipe_arr.append(simpy.Store(env))
            self.fifo_w_out_pipe_arr.append(simpy.Store(env)) 

            index = index + 1

        # instantiate the Base_Level object

        granularity = 1
        fifo_size = 128

        self.blevel = Base_level(env, line_clk_period, sys_clk_period, granularity, fifo_size, \
                        self.enq_pipe_cmd, self.enq_pipe_sts, self.deq_pipe_req, self.deq_pipe_dat, \
                        self.find_earliest_fifo_pipe_req, self.find_earliest_fifo_pipe_dat, \
                        self.fifo_r_in_pipe_arr, self.fifo_r_out_pipe_arr, self.fifo_w_in_pipe_arr, self.fifo_w_out_pipe_arr, \
                        fifo_write_latency=1, fifo_read_latency=1, \
                        fifo_check_latency=1, fifo_num=10, initial_vc=0)

        #self.ptr_list = list() # remove
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())

    def sched_enq(self):
        while True:
            (head_seg_ptr, meta_ptr, tuser) = yield self.ptr_out_pipe.get()
            #self.ptr_list.append((head_seg_ptr, meta_ptr, tuser))
            print ('@ {:.2f} - Enqueue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
            pkt_des = Packet_descriptior(head_seg_ptr, meta_ptr, tuser)
            print ('@ {} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
            self.enq_pipe_cmd.put(pkt_des)
            yield self.enq_pipe_sts.get()

    def sched_deq(self):
        while True:
            # wait for 10 cycles
            #for j in range(10):
            yield self.wait_sys_clks(1)
            
            if self.blevel.get_pkt_cnt() > 0:
                current_fifo_index = self.blevel.get_cur_fifo()
                self.find_earliest_fifo_pipe_req.put(current_fifo_index)
                deque_fifo = yield self.find_earliest_fifo_pipe_dat.get()
                self.deq_pipe_req.put(deque_fifo)
                pkt_des = yield self.deq_pipe_dat.get()
                print ('@ {} - From fifo {}, dequed pkt {} with rank = {}'.format(self.env.now, deque_fifo, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
                #((head_seg_ptr, meta_ptr, tuser)) = self.ptr_list.pop(0)
                head_seg_ptr = pkt_des.get_hdr_addr()
                meta_ptr = pkt_des.get_meta_addr()
                tuser = pkt_des.get_tuser()
                
                print ('@ {:.2f} - Dequeue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
                # submit read request
                self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))
