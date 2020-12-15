#!/usr/bin/env python

import simpy
from hwsim_utils import *

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe, pkt_mon_rdy):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe
        self.pkt_mon_rdy = pkt_mon_rdy

        self.ptr_list = list()
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())

    def sched_enq(self):
        while True:
            (head_seg_ptr, meta_ptr, tuser) = yield self.ptr_out_pipe.get()
            self.ptr_list.append((head_seg_ptr, meta_ptr, tuser))
            print ('@ {:.2f} - Enqueue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))

    def sched_deq(self):
        while True:
            # wait rdy from pkt mon
            yield self.pkt_mon_rdy.get()
            print ("got ready from pkt mon")

            # send packet when available
            while True:            
                if len(self.ptr_list) > 0:
                    ((head_seg_ptr, meta_ptr, tuser)) = self.ptr_list.pop(0)
                    print ('@ {:.2f} - Dequeue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
                    # submit read request
                    self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))
                    break
                else:
                    yield self.wait_sys_clks(1)
