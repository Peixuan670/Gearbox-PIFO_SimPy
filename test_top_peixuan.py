#!/usr/bin/env python

import simpy
from hwsim_utils import *
from pkt_gen import *
from packet_storage import *
from pkt_sched_peixuan import *
from pkt_mon import *

class Top_tb(HW_sim_object):
    def __init__(self, env, period):
        super(Top_tb, self).__init__(env, period)
        self.ptr_in_pipe = simpy.Store(env)
        self.ptr_out_pipe = simpy.Store(env)
        self.pkt_in_pipe = simpy.Store(env)
        self.pkt_out_pipe = simpy.Store(env)

        self.num_test_pkts = 10

        self.pkt_gen = Pkt_gen(env, period, self.pkt_in_pipe, self.num_test_pkts)
        self.pkt_store = Pkt_storage(env, period, self.pkt_in_pipe, self.pkt_out_pipe, self.ptr_in_pipe, self.ptr_out_pipe)
        self.pkt_sched = Pkt_sched(env, period, self.ptr_in_pipe, self.ptr_out_pipe)
        self.pkt_mon = Pkt_mon(env, period, self.pkt_out_pipe)
        
        self.run()

    def run(self):
        self.env.process(self.top_tb())

    def top_tb(self):
        yield self.env.timeout(1)
        
def main():
    env = simpy.Environment()
    period = 1
    # instantiate the testbench
    ps_tb = Top_tb(env, period)
    # run the simulation 
    env.run(until=250)

if __name__ == "__main__":
    main()

