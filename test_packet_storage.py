#!/usr/bin/env python

import simpy
from hwsim_utils import *
from packet_storage import *
from scapy.all import *

class Packet_storage_tb(HW_sim_object):
    def __init__(self, env, period):
        super(Packet_storage_tb, self).__init__(env, period)
        self.ptr_in_pipe = simpy.Store(env)
        self.ptr_out_pipe = simpy.Store(env)
        self.pkt_in_pipe = simpy.Store(env)
        self.pkt_out_pipe = simpy.Store(env)

        self.ps = Pkt_storage(env, period, self.pkt_in_pipe, self.pkt_out_pipe, self.ptr_in_pipe, self.ptr_out_pipe)
        self.num_test_pkts = 10
        
        self.run()

    def run(self):
        self.env.process(self.rw_ps_sm())

    def rw_ps_sm(self):
        """
        Loop for number of test packets
            - Write pkt and metadata into packet storage
            - Read back head_seg_ptr and meta_ptr and store in a list
            - Wait 10 clocks
        Loop for number of test packets
            - Read head and meta pointers from list
            - Submit read request to packet storage using head_seg_ptr and meta_ptr
            - Wait 10 cycles
            - Read output pkt and meta data 
        """
        ptr_list = list()
        for i in range(self.num_test_pkts):
            # create the test packets
            pkt = Ether()/IP()/TCP()/'hello there pretty world!!!'
            rank = random.sample(range(0, 100), 1)
            pkt_id = i
            tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
            pkt_list = [(pkt, tuser)]
            for pkt, tuser in pkt_list:
                print ('@ {} - Writing to storage: {} || {}'.format(self.env.now, pkt.summary(), tuser))
                # write the pkt and metadata into storage
                self.pkt_in_pipe.put((pkt, tuser))
                # read head_seg_ptr and metadata_ptr
                (head_seg_ptr, meta_ptr) = yield self.ptr_out_pipe.get()
                ptr_list.append((head_seg_ptr, meta_ptr))
                print ('@ {} - Received pointers: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))

                # wait for 10 cycles
                for j in range(10):
                    yield self.wait_clock()

        i = 0
        for i in range(self.num_test_pkts): 
            ((head_seg_ptr, meta_ptr)) = ptr_list[i]
            print ('@ {} - submitting read request: head_seg_ptr = {} , meta_ptr = {}'.format(self.env.now, head_seg_ptr, meta_ptr))
            # submit read request
            self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))
            # wait to receive output pkt and metadata
            (pkt_out, tuser_out) = yield self.pkt_out_pipe.get()
            print ('@ {} - Received from storage: {} || {}'.format(self.env.now, pkt_out.summary(), tuser_out))

            # wait for 10 cycles
            for j in range(10):
                yield self.wait_clock()


def main():
    env = simpy.Environment()
    period = 1
    # instantiate the testbench
    ps_tb = Packet_storage_tb(env, period)
    # run the simulation 
    env.run(until=250)


if __name__ == "__main__":
    main()

