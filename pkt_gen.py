#!/usr/bin/env python

import simpy
from random import choice, randint
from string import ascii_uppercase
from scapy.all import *
from hwsim_utils import *

class Pkt_gen(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, pkt_out_pipe, flow_id, weight, quantum, num_pkts, burst_size):
        super(Pkt_gen, self).__init__(env, line_clk_period, sys_clk_period)
        self.pkt_out_pipe = pkt_out_pipe
        self.flow_id = flow_id
        self.weight = weight
        self.quantum = quantum
        self.num_pkts = num_pkts
        self.burst_size = burst_size
        
        self.run()

    def run(self):
        self.env.process(self.pkt_gen(self.flow_id))
                    
    def pkt_gen(self, flow_id):
        """
        Loop for number of test packets with backpressure off
            - Generate packet
            - Wait packet time including preamble and IFG
        """
        i = 0
        fin_time = 0
        while i < self.num_pkts:
            #j = 0
            burst_len = 0
            #while j < self.burst_size:
            pyld = ''.join(choice(ascii_uppercase) for k in range(randint(6, 1460)))
            # create the test packets
            pkt = Ether()/IP()/TCP()/Raw(load=pyld)
            fin_time = round((len(pkt)/self.quantum)/self.weight)
            pkt_id = (flow_id, i)
            tuser = Tuser(len(pkt), fin_time, pkt_id)
            burst_len += len(pkt)
            print ('@ {:.2f} - Send:    {} || {}'.format(self.env.now, pkt.summary(), tuser))

            # write the pkt and metadata into storage
            self.pkt_out_pipe.put((pkt, tuser))

            #j += 1
            i += 1
            if i == self.num_pkts:
                break
                    
            # wait a number of clock cycles equivalent to the transmission time of the burst of packets
            #for j in range(PREAMBLE + len(pkt) + IFG):
            #yield self.wait_line_clks(j*self.PREAMBLE + burst_len + j*self.IFG)
            #print ("f: {} - pkt end: {}".format(self.flow_id, self.env.now))
            yield self.wait_line_clks(self.PREAMBLE + burst_len + self.IFG)
            #print ("f: {} - IFG end: {}".format(self.flow_id, self.env.now))
            
            # Insert another random gap
            yield self.wait_line_clks(randint(0, 128)) # average gap is 64 bytes
            #print ("f: {} - rdm int end: {}".format(self.flow_id, self.env.now))
            
            

