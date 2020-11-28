#!/usr/bin/env python

import simpy
from hwsim_utils import *
from scapy.all import *

class Pkt_gen(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, pkt_in_pipe, num_pkts):
        super(Pkt_gen, self).__init__(env, line_clk_period, sys_clk_period)
        self.pkt_in_pipe = pkt_in_pipe
        self.num_pkts = num_pkts
        
        self.run()

    def run(self):
        self.env.process(self.pkt_gen())

    def pkt_gen(self):
        """
        Loop for number of test packets
            - Generate packet
            - Wait packet time including preamble and IFG
        """
        for i in range(self.num_pkts):
            # create the test packets
            pkt = Ether()/IP()/TCP()/'hello there pretty world!!!'
            rank = random.sample(range(0, 100), 1)[0]
            pkt_id = i
            tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
            #print ('@ {:.2f} - Send:    {} || {}'.format(self.env.now, pkt.summary(), tuser))
            # write the pkt and metadata into storage
            self.pkt_in_pipe.put((pkt, tuser))

            # wait for 10 cycles
            #for j in range(PREAMBLE + len(pkt) + IFG):
            yield self.wait_line_clks(self.PREAMBLE + len(pkt) + self.IFG)

