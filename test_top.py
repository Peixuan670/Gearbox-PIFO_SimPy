#!/usr/bin/env python

import simpy
from hwsim_utils import *
from pkt_gen import *
from pkt_mux import *
from packet_storage import *
from pkt_sched_bb import *
from pkt_mon import *

class Top_tb(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period):
        super(Top_tb, self).__init__(env, line_clk_period, sys_clk_period)
        self.num_flows = 4
        self.ptr_in_pipe = simpy.Store(env)
        self.ptr_out_pipe = simpy.Store(env)
        self.vc_upd_pipe = simpy.Store(env)
        self.pkt_gen_pipes = [simpy.Store(env)] * self.num_flows
        self.pkt_mux_pipe = simpy.Store(env)
        self.pkt_store_pipe = simpy.Store(env)
        self.pkt_mon_rdy = simpy.Store(env)

        self.weights = [0.65, 0.20, 0.10, 0.05]
        self.quantum = 64 # bytes
        self.num_test_pkts = [25, 25, 25, 25]
        self.burst_size = [5, 5, 5, 5]

        self.pkt_gen = list()
        for f in range(self.num_flows):
            self.pkt_gen = Pkt_gen(env, line_clk_period, sys_clk_period, self.vc_upd_pipe, \
                                   self.pkt_gen_pipes[f], f, self.weights[f], self.quantum, \
                                   self.num_test_pkts[f], self.burst_size[f])
        self.pkt_mux = Pkt_mux(env, line_clk_period, sys_clk_period, self.pkt_gen_pipes, self.pkt_mux_pipe)
        self.pkt_store = Pkt_storage(env, line_clk_period, sys_clk_period, self.pkt_mux_pipe, \
                                     self.pkt_store_pipe, self.ptr_in_pipe, self.ptr_out_pipe)
        self.pkt_sched = Pkt_sched(env, line_clk_period, sys_clk_period, self.ptr_in_pipe, \
                                  self.ptr_out_pipe, self.pkt_mon_rdy)
        self.pkt_mon = Pkt_mon(env, line_clk_period, sys_clk_period, self.pkt_store_pipe, \
                               self.num_flows, self.num_test_pkts, self.pkt_mon_rdy)
        
        self.vc = 0
        
        self.run()

    def run(self):
        self.env.process(self.top_tb())

    def top_tb(self):
        while True:
            #print ("Top VC: {0}".format(self.vc))
            for i in range(self.num_flows):
                self.vc_upd_pipe.put(self.vc)
            yield self.env.timeout(1000)
            self.vc += 1
        
def main():
    env = simpy.Environment(0.0)
    line_clk_period = 0.1 * 8 # 0,1 ns/bit * 8 bits
    sys_clk_period = 5 # ns (200 MHz)
    # instantiate the testbench
    ps_tb = Top_tb(env, line_clk_period, sys_clk_period)
    # run the simulation 
    env.run(until=100000)

if __name__ == "__main__":
    main()

