#!/usr/bin/env python

import simpy
from hwsim_utils import *
#from GearboxI_proto_II_jump_VC import Gearbox_I
from GearboxII_new_jupmVC import Gearbox_II
from packet import Packet_descriptior
from queues import *

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe, pkt_mon_rdy, vc_upd_pipe, drop_pipe, verbose):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe
        self.pkt_mon_rdy = pkt_mon_rdy
        self.verbose = verbose

        # 12312020 Peixuan: test vc
        self.vc_upd_pipe = vc_upd_pipe
        #self.blevel_vc_upd_pipe = simpy.Store(env) # 01202021 Peixuan blevel vc
        self.gearbox_vc_upd_pipe = simpy.Store(env) # 01202021 Peixuan gearbox vc
        self.drop_pipe = drop_pipe
        
        self.vc = 0

        # gearbox enque pipe
        self.gb_enq_pipe_cmd = simpy.Store(env)
        self.gb_enq_pipe_sts = simpy.Store(env)
        self.gb_deq_pipe_req = simpy.Store(env)
        self.gb_deq_pipe_dat = simpy.Store(env)

        fifo_num_list = [10, 10, 10]
        granularity_list = [1, 10, 100]
        fifo_size_list = [128, 128, 128]
        pifo_size_list = [8, 8, 8]
        pifo_thresh_list = [4, 4, 4]

        # instantiate the Base_Level object
        
        self.gearbox = Gearbox_II(env, line_clk_period, sys_clk_period, \
                                self.gb_enq_pipe_cmd, self.gb_enq_pipe_sts, self.gb_deq_pipe_req, self.gb_deq_pipe_dat, \
                                self.gearbox_vc_upd_pipe, self.drop_pipe, \
                                granularity_list, fifo_num_list, fifo_size_list, pifo_size_list, pifo_thresh_list,\
                                fifo_check_latency=1, initial_vc=0)
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())
        self.env.process(self.vc_update_p())

    def sched_enq(self):
        prev_fin_time_lst = [0] * 1024 * 32
        tmp_tuser = Tuser(0, 0, (0, 0))     # We need a new tmp_user each time
        while True:
            desc_in = yield self.ptr_out_pipe.get()

            if self.verbose:
                print ('@ {:.2f} - Enqueue: tuser = {}'.format(self.env.now, desc_in))
            pkt_len = desc_in[0]
            rank = desc_in[1]
            flow_id = desc_in[2]
            pkt_id = desc_in[3]
            fin_time = max(prev_fin_time_lst[flow_id], self.vc) + rank

            tmp_tuser = Tuser(0, 0, (0, 0))     # We need a new tmp_user each time, Peixuan 05172021

            tmp_tuser.pkt_len = pkt_len
            tmp_tuser.rank = fin_time
            tmp_tuser.pkt_id = (flow_id, pkt_id)

            if self.verbose:
                print ('@ {:.2f} - Enqueue: desc_out = {}'.format(self.env.now, tmp_tuser))
            enq_pkt_des = Packet_descriptior(0, 0, tmp_tuser)
            if self.verbose:
                print ('@ {} - pushed pkt {} with rank = {}'.format(self.env.now, enq_pkt_des.get_uid(), enq_pkt_des.get_finish_time(debug=True)))

            self.gb_enq_pipe_cmd.put(enq_pkt_des)

            enq_success = yield self.gb_enq_pipe_sts.get()  # Enqued: return True; pkt dropped: return False

            if enq_success:
                prev_fin_time_lst[flow_id] = fin_time # update prev_fin_time

    def sched_deq(self):
        while True:
            # wait rdy from pkt mon
            yield self.pkt_mon_rdy.get()
            print ("got ready from pkt mon")

            while True:
                # wait for 10 cycles
                #for j in range(10):
                yield self.wait_sys_clks(1)

                if self.gearbox.get_pkt_cnt() > 0:

                    self.gb_deq_pipe_req.put(1)     # put anything here to request for a deque
                    data = yield self.gb_deq_pipe_dat.get()
                    deq_pkt_des = data[0] # TODO: why this data is a tuple <pkt, 0>
                    if self.verbose:
                        print ('@ {} - From Gearbox dequed pkt {} with rank = {}'.format(self.env.now, deq_pkt_des.get_uid(), deq_pkt_des.get_finish_time(debug=True)))

                    head_seg_ptr = deq_pkt_des.get_hdr_addr()
                    meta_ptr = deq_pkt_des.get_meta_addr()
                    tuser = deq_pkt_des.get_tuser()
                
                    if self.verbose:
                        print ('@ {:.2f} - Dequeue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
                    # submit read request
                    self.ptr_in_pipe.put((head_seg_ptr, meta_ptr, tuser))
    
    def vc_update_p(self):
        while True:
            updated_vc = yield self.gearbox_vc_upd_pipe.get()
            self.vc = updated_vc
            if self.verbose:
                print ("updated pkt_sched vc = {}".format(self.vc))


