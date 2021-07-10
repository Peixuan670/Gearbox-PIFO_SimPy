#!/usr/bin/env python

import os
import simpy
from hwsim_utils import *
#from pkt_gen import *
from desc_gen import *
#from pkt_mux import *
#from packet_storage import *
#from pkt_sched_blevel import *
#from pkt_sched_gearbox import *
from pkt_sched_gearboxII import *
from pkt_mon import *

class Top_tb(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period):
        super(Top_tb, self).__init__(env, line_clk_period, sys_clk_period)
#        self.ptr_in_pipe = simpy.Store(env)
        self.pcap_desc_pipe = simpy.Store(env)
        self.drop_pipe = simpy.Store(env)
        self.sched_vc_pipe = simpy.Store(env) # 12312020 Peixuan test
#        self.pkt_mux_pipe = simpy.Store(env)
        self.sched_desc_pipe = simpy.Store(env)
        self.mon_info_pipe = simpy.Store(env)
        self.pkt_mon_rdy = simpy.Store(env)

        pcap_file_name = "smallFlows.pcap"
        #pcap_file_name = "test.pcap"
        base_file_name = os.path.splitext(pcap_file_name)[0]
        #rate_tuple_list = [(10,2), (10,0.5)]
        rate_tuple_list = [(20000,20), (20000,0.05)]
        #rate_tuple_list = [(100,20), (100,0.05)]
        #rate_tuple_list = [(1000,200), (1000,0.005)]
        quantum = 1

#        self.bit_rates = [1 * 10**9, 1 * 10**9, 1 * 10**9, 1 * 10**9]
#        self.weights = [1, 1, 1, 1]
#        self.quantum = 64 # bytes
#        self.num_test_pkts = [50, 50, 50, 50]

#        self.pkt_gen = list()
#        for f in range(self.num_flows):
#            self.pkt_gen = Pkt_gen(env, line_clk_period, sys_clk_period, \
#                                   self.pkt_gen_pipes[f], f, self.bit_rates[f], self.weights[f], self.quantum, \
#                                   self.num_test_pkts[f])
#        self.pkt_mux = Pkt_mux(env, line_clk_period, sys_clk_period, self.pkt_gen_pipes, self.pkt_mux_pipe)
#        self.pkt_store = Pkt_storage(env, line_clk_period, sys_clk_period, self.pkt_mux_pipe, \
#                                     self.pkt_store_pipe, self.ptr_in_pipe, self.ptr_out_pipe, self.drop_pipe)

        
        self.desc_gen = Desc_gen(env, line_clk_period, sys_clk_period, base_file_name, \
                                 self.pcap_desc_pipe, self.mon_info_pipe, rate_tuple_list, quantum, verbose=False)
        self.pkt_sched = Pkt_sched(env, line_clk_period, sys_clk_period, self.sched_desc_pipe, \
                                  self.pcap_desc_pipe, self.pkt_mon_rdy, self.sched_vc_pipe, self.drop_pipe, verbose=False)
        self.pkt_mon = Pkt_mon(env, line_clk_period, sys_clk_period, self.sched_desc_pipe, self.drop_pipe,\
                               self.mon_info_pipe, self.pkt_mon_rdy, verbose=False)
        
        self.vc = 0
        
        self.run()

    def run(self):
        self.env.process(self.top_tb())

    def top_tb(self):
        while True:
            updated_vc = yield self.sched_vc_pipe.get()
            self.vc = updated_vc
            if self.verbose:
                print ("Top VC: {0}".format(self.vc))
                print("updated top vc = {}".format(self.vc)) # Peixuan debug
        
def main():
    env = simpy.Environment(0.0)
    line_clk_period = 0.1 * 8 # 0,1 ns/bit * 8 bits
    sys_clk_period = 5 # ns (200 MHz)
    # instantiate the testbench
    ps_tb = Top_tb(env, line_clk_period, sys_clk_period)
    # run the simulation 
    env.run(until=100000000)
    #env.run(until=30000000)
    #env.run(until=100000)

if __name__ == "__main__":
    main()

