#!/usr/bin/env python

import simpy
from random import choice, randint
from string import ascii_uppercase
from scapy.all import *
from hwsim_utils import *

class Pkt_gen(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, vc_upd_pipe, pkt_in_pipe, num_pkts, burst_size):
        super(Pkt_gen, self).__init__(env, line_clk_period, sys_clk_period)
        self.vc_upd_pipe = vc_upd_pipe
        self.pkt_in_pipe = pkt_in_pipe
        self.num_pkts = num_pkts
        self.burst_size = burst_size
        
        self.vc = 0
        self.run()

    def run(self):
        self.env.process(self.vc_upd())
        self.env.process(self.pkt_gen())

    def vc_upd(self):
        """ wait for VC update
            add VC update to VC
        """
        while True:
            vc_incr = yield self.vc_upd_pipe.get()
            self.vc += vc_incr
            #print ("VC Update: {}".format(self.vc))
                    
    def pkt_gen(self):
        """
        Loop for number of test packets with backpressure off
            - Generate packet
            - Wait packet time including preamble and IFG
        """
        pkt_lst = list()
        i = 0
        while i < self.num_pkts:
            j = 0
            burst_len = 0
            while j < self.burst_size:
                pyld = ''.join(choice(ascii_uppercase) for k in range(randint(6, 1460)))
                # create the test packets
                pkt = Ether()/IP()/TCP()/Raw(load=pyld)
                rank = self.vc + random.sample(range(0, 100), 1)[0]
                pkt_id = i
                tuser = Tuser(len(pkt), 0b00000001, 0b00000100, rank, pkt_id)
                burst_len += len(pkt)
                print ('@ {:.2f} - VC: {} - Send:    {} || {}'.format(self.env.now, self.vc, pkt.summary(), tuser))
                pkt_lst.append((pkt, tuser))

                # write the pkt and metadata into storage
                self.pkt_in_pipe.put((pkt, tuser))

                j += 1
                i += 1
                if i == self.num_pkts:
                    break
                    
            # wait a number of clock cycles equivalent to the transmission time of the burst of packets
            #for j in range(PREAMBLE + len(pkt) + IFG):
            yield self.wait_line_clks(j*self.PREAMBLE + burst_len + j*self.IFG)
            

