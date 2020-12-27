#!/usr/bin/env python

import simpy
from hwsim_utils import *
from packet_storage import *
from scapy.all import *

class Pkt_mon(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, pkt_out_pipe, pkt_mon_rdy):
        super(Pkt_mon, self).__init__(env, line_clk_period, sys_clk_period)
        self.pkt_out_pipe = pkt_out_pipe
        self.pkt_mon_rdy = pkt_mon_rdy
        
        self.pkt_mon_lst = [(0, None)] * 2
        self.run()

    def run(self):
        self.env.process(self.pkt_mon_queue())
        self.env.process(self.pkt_mon_sm())

    def pkt_mon_queue(self):
        i = 0
        while True:
            # signal pkt mon ready to scheduler
            self.pkt_mon_rdy.put(1)
            # wait to receive output pkt and metadata
            (pkt_out, tuser_out) = yield self.pkt_out_pipe.get()
            # store packet and metadata in list
            self.pkt_mon_lst[i] = (1, (pkt_out, tuser_out))
            # flip index
            if i == 0:
                i = 1
            else:
                i = 0
            # Wait until there's room in the queue
            while (self.pkt_mon_lst[0][0] == 1 and self.pkt_mon_lst[1][0] == 1):
                yield self.wait_sys_clks(1)
                
    def pkt_mon_sm(self):
        i = 0
        while True:
            # Wait until there's a packet in the queue
            while (self.pkt_mon_lst[i][0] == 0):
                yield self.wait_sys_clks(1)
            # get packet from queue
            (pkt_out, tuser_out) = self.pkt_mon_lst[i][1]
            self.pkt_mon_lst[i] = (0, (0, 0))
            print ('@ {:.2f} - Receive: {} || {}'.format(self.env.now, pkt_out.summary(), tuser_out))
            # wait number of clocks corresponding to packet preamble, packet length and IFG
            yield self.wait_line_clks(self.PREAMBLE + pkt_out.len + self.IFG)
            # flip index
            if i == 0:
                i = 1
            else:
                i = 0

