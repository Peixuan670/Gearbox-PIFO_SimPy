#!/usr/bin/env python

import random
import simpy
from hwsim_utils import *
from scapy.all import *

"""
Testbench for the PIFO object
"""
class BLevel_tb(HW_sim_object):
    def __init__(self, env, period, fifo_num=10):
        super(BLevel_tb, self).__init__(env, period)

        self.fifo_num = fifo_num

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

        self.blevel = Base_level(env, period, granularity, fifo_size, self.fifo_r_in_pipe_arr, self.fifo_r_out_pipe_arr, \
        self.fifo_w_in_pipe_arr, self.fifo_w_out_pipe_arr, fifo_write_latency=1, fifo_read_latency=1, \
        fifo_check_latency=1, fifo_num=10, initial_vc=0)

        self.run()

    def run(self):
        """
        Register the testbench's processes with the simulation environment
        """
        self.env.process(self.rw_blevel_sm())

    def rw_blevel_sm(self):
        """
        State machine to push all test data then read it back
        """

        # generate random pkts: TODO: is this okay?
        pkt_list = []

        for i in range(self.num_test_pkts):
            pkt = Ether()/IP()/TCP()/'hello there pretty world!!!'
            rank = random.sample(range(0, 10), 1)[0]
            pkt_id = i
            tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
            cur_pkt = Packet_descriptior(pkt_id, tuser) # TODO: what should be the address looks like
            # Anthony: address comes from the pkt_storage (managed by it). It's a number.
            pkt_list.append(cur_pkt)

        # push all data
        print ('Start enquing packets')
        for pkt_des in pkt_list:
            print ('@ {:04d} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time()))

            #yield self.blevel.enque(pkt_des)
            self.blevel.enque(pkt_des)
            for i in range(2):
                yield self.wait_clock()

            #self.pifo_w_in_pipe.put(pkt_des)
            #((done, popped_data, popped_data_valid)) = yield self.pifo_w_out_pipe.get() # tuple
            #if popped_data_valid:
            #    print ('@ {:04d} - popped pkt {} with rank = {}'.format(self.env.now, popped_data.get_uid(), popped_data.get_finish_time()))
            

        # pop all items
        print ('Start dequing packets')
        for i in range(len(pkt_list)):
            # submit pop request (value in put is a don't care)
            pkt_des = self.blevel.deque_earliest_pkt()
            print ('@ {:04d} - dequed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time()))


def main():
    # create the simulation environment
    env = simpy.Environment()
    period = 1 # amount of simulation time / clock cycle
    blevel_tb = BLevel_tb(env, period)
 
    # run the simulation for 100 simulation seconds (100 clock cycles)
    env.run(until=100)


if __name__ == "__main__":
    main()

