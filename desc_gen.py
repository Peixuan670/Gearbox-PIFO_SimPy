import simpy
#import argparse
import os
import sys
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from hwsim_utils import *

class Desc_gen(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, base_file_name, pcap_desc_pipe, mon_info_pipe):
        super(Desc_gen, self).__init__(env, line_clk_period, sys_clk_period)
        self.desc_file_name = base_file_name + '_desc.txt'
        self.info_file_name = base_file_name + '_info.txt'
        self.pcap_desc_pipe = pcap_desc_pipe
        self.mon_info_pipe = mon_info_pipe
        
        if not os.path.isfile(self.desc_file_name):
            print('"{}" does not exist'.format(self.desc_file_name), file=sys.stderr)
            sys.exit(-1)

        if not os.path.isfile(self.info_file_name):
            print('"{}" does not exist'.format(self.info_file_name), file=sys.stderr)
            sys.exit(-1)

        print('Opening {}...'.format(self.desc_file_name))
        self.f_desc = open(self.desc_file_name, 'r')
        
        f_info = open(self.info_file_name, 'r')
        num_flows = int(f_info.readline())
        print('Number of flows: {}'.format(num_flows))
        num_pkts = []
        for f in range(num_flows):
            num_pkts.append(int(f_info.readline()))
        self.mon_info_pipe.put((num_flows, num_pkts))
        self.run()

    def run(self):
        self.env.process(self.process_desc(self.f_desc))
        
    def process_desc(self, f_desc):  
        for line in f_desc:
            desc_items = line.split(',')
            pkt_len = int(desc_items[0])
            fin_time = int(desc_items[1])
            flow_id = int(desc_items[2])
            pkt_id = int(desc_items[3])

            desc_tuple = (pkt_len, fin_time, flow_id, pkt_id)
            self.pcap_desc_pipe.put(desc_tuple)
            pkt_time = self.PREAMBLE + pkt_len + self.IFG
            yield self.wait_line_clks(pkt_time)

    