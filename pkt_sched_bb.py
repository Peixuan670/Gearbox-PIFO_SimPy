#!/usr/bin/env python

import simpy
from hwsim_utils import *

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe

        self.ptr_list = list()
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())

    def sched_enq(self):
        while True:
            (head_seg_ptr, meta_ptr) = yield self.ptr_out_pipe.get()
            self.ptr_list.append((head_seg_ptr, meta_ptr))
            print ('@ {:.2f} - Enqueue: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))

    def sched_deq(self):
        while True:
            # wait for 10 cycles
            #for j in range(10):
            yield self.wait_sys_clks(1)
            
            if len(self.ptr_list) > 0:
                ((head_seg_ptr, meta_ptr)) = self.ptr_list.pop(0)
                print ('@ {:.2f} - Dequeue: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))
                # submit read request
                self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))
