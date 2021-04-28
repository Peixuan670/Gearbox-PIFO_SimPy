import simpy
import argparse
import os
import sys
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP

def process_pcap(pcap_file_name):
    count = 0
    tcp_ip_pkt_count = 0
    ack_only_pkt_count = 0
    flow_list = []
    pkt_id_list = []
    weight = 1
    
    base_name = os.path.splitext(pcap_file_name)[0]
    f_desc = open(base_name+'_desc.txt', 'w')
    for (pkt_data, pkt_metadata,) in RawPcapReader(pcap_file_name):
        count += 1
    
        ether_pkt = Ether(pkt_data)
        if 'type' not in ether_pkt.fields:
            # LLC frames will have 'len' instead of 'type'.
            # We disregard those
            continue

        if ether_pkt.type != 0x0800:
            # disregard non-IPv4 packets
            continue

        ip_pkt = ether_pkt[IP]
        
#        if ip_pkt.proto != 6 and ip_pkt.proto != 17:
        if ip_pkt.proto != 6:
            # Ignore non-TCP and non-UDP packet
            continue

        tcp_pkt = ip_pkt[TCP]

        pkt_len = max(len(ether_pkt), 64)    
        fin_time = pkt_len/weight

        five_tuple = (ip_pkt.src, tcp_pkt.sport, ip_pkt.dst, tcp_pkt.dport, ip_pkt.proto);
        try:
            # get flow_id for 5-tuple
            flow_id = flow_list.index(five_tuple)
            # get and update pkt_id for flow 
            pkt_id = pkt_id_list[flow_id]
            pkt_id += 1
            pkt_id_list[flow_id] = pkt_id
        except ValueError:
            flow_list.append(five_tuple)
            flow_id = flow_list.index(five_tuple)
            pkt_id_list.append(1)
            pkt_id = 1
            
        desc_str = str(pkt_len)+','+str(int(fin_time))+','+str(flow_id)+','+str(pkt_id)+'\n'
        f_desc.write(desc_str)
        
        tcp_ip_pkt_count += 1

        # Determine the TCP payload length. IP fragmentation will mess up this
        # logic, so first check that this is an unfragmented packet
        #if (ip_pkt.flags == 'MF') or (ip_pkt.frag != 0):
        #    print('No support for fragmented IP packets')
        #    return False
        
        #tcp_payload_len = ip_pkt.len - (ip_pkt.ihl * 4) - (tcp_pkt.dataofs * 4)

        # Check if this packet is an Ack only (with no data)
        #if 'A' in str(tcp_pkt.flags) and tcp_payload_len == 0:
        #    ack_only_pkt_count += 1

    f_desc.close()
    
    print('{} contains {} packets ({} TCP/IP packets)'.format(file_name, count, tcp_ip_pkt_count))
    print('There are {} flows'.format(len(flow_list)))
#    print('There are {} ack only packets'.format(ack_only_pkt_count))
    f_info = open(base_name+'_info.txt', 'w')
    f_info.write(str(len(flow_list))+'\n')
    for flow_id in range(len(pkt_id_list)):
        print (pkt_id_list[flow_id])
        f_info.write(str(pkt_id_list[flow_id])+'\n')
    f_info.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PCAP reader')
    parser.add_argument('--pcap', metavar='<pcap file name>',
                        help='pcap file to parse', required=True)
    args = parser.parse_args()
    
    file_name = args.pcap
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    process_pcap(file_name)
    sys.exit(0)
    