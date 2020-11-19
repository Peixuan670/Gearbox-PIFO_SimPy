#!/usr/bin/env python

import random
import simpy
from hwsim_utils import *
from scapy.all import *

"""
Testbench for the PIFO object
"""
class PIFO_tb(HW_sim_object):
    def __init__(self, env, period):
        super(PIFO_tb, self).__init__(env, period)

        # number of tesing packets
        self.num_test_pkts = 20

        # create the pipes used for communication with the PIFO object
        self.pifo_r_in_pipe = simpy.Store(env)
        self.pifo_r_out_pipe = simpy.Store(env)
        self.pifo_w_in_pipe = simpy.Store(env)
        self.pifo_w_out_pipe = simpy.Store(env)

        # instantiate the PIFO object
        self.pifo_maxsize = 10
        self.pifo = PIFO(env, period, self.pifo_r_in_pipe, self.pifo_r_out_pipe, \
                         self.pifo_w_in_pipe, self.pifo_w_out_pipe, maxsize=self.pifo_maxsize,\
                         write_latency=1, read_latency=2, init_items=[])

        self.run()

    def run(self):
        """
        Register the testbench's processes with the simulation environment
        """
        self.env.process(self.rw_pifo_sm())

    def rw_pifo_sm(self):
        """
        State machine to push all test data then read it back
        """

        # generate random pkts: TODO: is this okay?
        pkt_list = []

        for i in range(self.num_test_pkts):
            pkt = Ether()/IP()/TCP()/'hello there pretty world!!!'
            rank = random.sample(range(0, 10), 1)
            pkt_id = i
            tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
            cur_pkt = Packet_descriptior(pkt_id, tuser) # TODO: what should be the address looks like
            # Anthony: address comes from the pkt_storage (managed by it). It's a number.
            pkt_list.append(cur_pkt)

        # push all data
        print ('Start enquing packets')
        for pkt_des in pkt_list:
            print ('@ {:04d} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time()))
            self.pifo_w_in_pipe.put(pkt_des)
            ((done, popped_data, popped_data_valid)) = yield self.pifo_w_out_pipe.get() # tuple
            if popped_data_valid:
                print ('@ {:04d} - popped pkt {} with rank = {}'.format(self.env.now, popped_data.get_uid(), popped_data.get_finish_time()))
            

        # pop all items
        print ('Start dequing packets')
        for i in range(min(self.pifo_maxsize,len(pkt_list))):
            # submit pop request (value in put is a don't care)
            self.pifo_r_in_pipe.put(1) 
            pkt_des = yield self.pifo_r_out_pipe.get()
            print ('@ {:04d} - dequed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time()))


def main():
    # create the simulation environment
    env = simpy.Environment()
    period = 1 # amount of simulation time / clock cycle
    pifo_tb = PIFO_tb(env, period)
 
    # run the simulation for 100 simulation seconds (100 clock cycles)
    env.run(until=100)


if __name__ == "__main__":
    main()

