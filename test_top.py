#!/usr/bin/env python

import simpy
from hwsim_utils import *
from pkt_gen import *
from packet_storage import *
from pkt_sched_bb import *
from pkt_mon import *

class Top_tb(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period):
        super(Top_tb, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = simpy.Store(env)
        self.ptr_out_pipe = simpy.Store(env)
        self.vc_upd_pipe = simpy.Store(env)
        self.bp_upd_pipe = simpy.Store(env)
        self.pkt_in_pipe = simpy.Store(env)
        self.pkt_out_pipe = simpy.Store(env)

        self.num_test_pkts = 10

        self.pkt_gen = Pkt_gen(env, line_clk_period, sys_clk_period, self.vc_upd_pipe, \
                               self.bp_upd_pipe, self.pkt_in_pipe, self.num_test_pkts)
        self.pkt_store = Pkt_storage(env, line_clk_period, sys_clk_period, self.pkt_in_pipe, \
                                     self.pkt_out_pipe, self.ptr_in_pipe, self.ptr_out_pipe)
        self.pkt_sched = Pkt_sched(env, line_clk_period, sys_clk_period, self.ptr_in_pipe, \
                                  self.ptr_out_pipe)
        self.pkt_mon = Pkt_mon(env, line_clk_period, sys_clk_period, self.pkt_out_pipe)
        
        self.vc = 0
        self.bp = 0
        
        self.run()

    def run(self):
        self.env.process(self.top_tb())

    def top_tb(self):
        while True:
            self.vc_upd_pipe.put(self.env.now)
            yield self.env.timeout(1)
        
def main():
    env = simpy.Environment(0.0)
    line_clk_period = 0.1 * 8 # 0,1 ns/bit * 8 bits
    sys_clk_period = 5 # ns (200 MHz)
    # instantiate the testbench
    ps_tb = Top_tb(env, line_clk_period, sys_clk_period)
    # run the simulation 
    env.run(until=10000)

if __name__ == "__main__":
    main()

