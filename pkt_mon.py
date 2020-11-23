#!/usr/bin/env python

import simpy
from hwsim_utils import *
from packet_storage import *
from scapy.all import *

class Pkt_mon(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, pkt_out_pipe):
        super(Pkt_mon, self).__init__(env, line_clk_period, sys_clk_period)
        self.pkt_out_pipe = pkt_out_pipe
        
        self.run()

    def run(self):
        self.env.process(self.pkt_mon_sm())

    def pkt_mon_sm(self):
        """
            - Read output pkt and meta data 
        """
        while True:
            # wait to receive output pkt and metadata
            (pkt_out, tuser_out) = yield self.pkt_out_pipe.get()
            print ('@ {:.2f} - Receive: {} || {}'.format(self.env.now, pkt_out.summary(), tuser_out))
            #yield self.wait_line_clks(self.PREAMBLE + pkt_out.len + self.IFG)
            #yield self.wait_line_clks(self.PREAMBLE + 81 + self.IFG)

