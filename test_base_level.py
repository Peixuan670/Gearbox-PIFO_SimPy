#!/usr/bin/env python

import random
import simpy
from hwsim_utils import *
from scapy.all import *
from base_level import Base_level
from packet import Packet_descriptior
from queues import *

"""
Testbench for the PIFO object
"""
class BLevel_tb(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, fifo_num=10):
        super(BLevel_tb, self).__init__(env, line_clk_period, sys_clk_period)
        self.enq_pipe_cmd = simpy.Store(env)
        self.enq_pipe_sts = simpy.Store(env)
        self.deq_pipe_req = simpy.Store(env)
        self.deq_pipe_dat = simpy.Store(env)
        self.find_earliest_fifo_pipe_req = simpy.Store(env)
        self.find_earliest_fifo_pipe_dat = simpy.Store(env)
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

        self.blevel = Base_level(env, line_clk_period, sys_clk_period, granularity, fifo_size, \
                        self.enq_pipe_cmd, self.enq_pipe_sts, self.deq_pipe_req, self.deq_pipe_dat, \
                        self.find_earliest_fifo_pipe_req, self.find_earliest_fifo_pipe_dat, \
                        self.fifo_r_in_pipe_arr, self.fifo_r_out_pipe_arr, self.fifo_w_in_pipe_arr, self.fifo_w_out_pipe_arr, \
                        fifo_write_latency=1, fifo_read_latency=1, \
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
            print ('@ {} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))

            #yield self.blevel.enque(pkt_des)
            #self.blevel.enque(pkt_des)
            self.enq_pipe_cmd.put(pkt_des)
            yield self.enq_pipe_sts.get()
            #self.pifo_w_in_pipe.put(pkt_des)
            #((done, popped_data, popped_data_valid)) = yield self.pifo_w_out_pipe.get() # tuple
            #if popped_data_valid:
            #    print ('@ {:04d} - popped pkt {} with rank = {}'.format(self.env.now, popped_data.get_uid(), popped_data.get_finish_time()))


        # pop all items
        print ('Start dequing packets')
        for i in range(len(pkt_list)):
            # submit pop request (value in put is a don't care)
            #pkt_des = self.blevel.deque_earliest_pkt()
            current_fifo_index = self.blevel.get_cur_fifo()
            self.find_earliest_fifo_pipe_req.put(current_fifo_index)
            deque_fifo = yield self.find_earliest_fifo_pipe_dat.get()
            self.deq_pipe_req.put(deque_fifo)
            pkt_des = yield self.deq_pipe_dat.get()
            print ('@ {} - From fifo {}, dequed pkt {} with rank = {}'.format(self.env.now, deque_fifo, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))    
 
        yield self.env.timeout(1)

def main():
    env = simpy.Environment(0.0)
    line_clk_period = 0.1 * 8 # 0,1 ns/bit * 8 bits
    sys_clk_period = 5 # ns (200 MHz)
    # instantiate the testbench
    blevel_tb = BLevel_tb(env, line_clk_period, sys_clk_period)
    # run the simulation 
    env.run(until=1000)


if __name__ == "__main__":
    main()

