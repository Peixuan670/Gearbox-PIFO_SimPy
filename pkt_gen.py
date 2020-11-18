#!/usr/bin/env python

import simpy
from hwsim_utils import *
from scapy.all import *

class Pkt_gen(HW_sim_object):
    def __init__(self, env, period, pkt_in_pipe, num_pkts):
        super(Pkt_gen, self).__init__(env, period)
        self.pkt_in_pipe = pkt_in_pipe
        self.num_pkts = num_pkts
        
        self.run()

    def run(self):
        self.env.process(self.pkt_gen())

    def pkt_gen(self):
        """
        Loop for number of test packets
            - Generate packet
            - Wait 10 clocks
        """
        for i in range(self.num_pkts):
            # create the test packets
            pkt = Ether()/IP()/TCP()/'hello there pretty world!!!'
            rank = random.sample(range(0, 100), 1)
            pkt_id = i
            tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
            print ('@ {} - Send:    {} || {}'.format(self.env.now, pkt.summary(), tuser))
            # write the pkt and metadata into storage
            self.pkt_in_pipe.put((pkt, tuser))

            # wait for 10 cycles
            for j in range(10):
                yield self.wait_clock()

