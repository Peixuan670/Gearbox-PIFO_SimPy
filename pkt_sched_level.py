#!/usr/bin/env python

import simpy
from hwsim_utils import *
from level_draft import Level
from packet import Packet_descriptior
from queues import *

class Pkt_sched(HW_sim_object):
    def __init__(self, env, line_clk_period, sys_clk_period, ptr_in_pipe, ptr_out_pipe):
        super(Pkt_sched, self).__init__(env, line_clk_period, sys_clk_period)
        self.ptr_in_pipe = ptr_in_pipe
        self.ptr_out_pipe = ptr_out_pipe

        # level
        self.enq_pipe_cmd = simpy.Store(env)
        self.enq_pipe_sts = simpy.Store(env)
        self.deq_pipe_req = simpy.Store(env)
        self.deq_pipe_dat = simpy.Store(env)
        self.find_earliest_fifo_pipe_req = simpy.Store(env)
        self.find_earliest_fifo_pipe_dat = simpy.Store(env)
        self.fifo_num = 10

        # reload
        self.reload_cmd = simpy.Store(env)
        self.reload_sts= simpy.Store(env)

        # number of tesing packets
        self.num_test_pkts = 30

        # create the pipes used for communication with the Level object

        # Initialize PIFO read/write handle

        self.pifo_r_in_pipe = simpy.Store(env)
        self.pifo_r_out_pipe = simpy.Store(env)
        self.pifo_w_in_pipe = simpy.Store(env)
        self.pifo_w_out_pipe = simpy.Store(env)

        # Initialize FIFO array and read/write handle
        
        self.fifo_r_in_pipe_arr = []
        self.fifo_r_out_pipe_arr = []
        self.fifo_w_in_pipe_arr = []
        self.fifo_w_out_pipe_arr = []
        
        index = 0
        while (index < self.fifo_num):
            self.fifo_r_in_pipe_arr.append(simpy.Store(env))
            self.fifo_r_out_pipe_arr.append(simpy.Store(env))
            self.fifo_w_in_pipe_arr.append(simpy.Store(env))
            self.fifo_w_out_pipe_arr.append(simpy.Store(env)) 

            index = index + 1

        # instantiate the Base_Level object

        granularity = 10
        fifo_size = 128

        pifo_thresh = 5
        pifo_size = 10 

        self.level = Level(env, line_clk_period, sys_clk_period, granularity, fifo_size, \
                        pifo_thresh, pifo_size, \
                        self.enq_pipe_cmd, self.enq_pipe_sts, self.deq_pipe_req, self.deq_pipe_dat, \
                        self.find_earliest_fifo_pipe_req, self.find_earliest_fifo_pipe_dat, \
                        self.fifo_r_in_pipe_arr, self.fifo_r_out_pipe_arr, self.fifo_w_in_pipe_arr, self.fifo_w_out_pipe_arr, \
                        self.pifo_r_in_pipe, self.pifo_r_out_pipe, self.pifo_w_in_pipe, self.pifo_w_out_pipe,\
                        fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10,\
                        pifo_write_latency=1, pifo_read_latency=1, initial_vc=0)

        #self.ptr_list = list() # remove
        
        self.run()

    def run(self):
        self.env.process(self.sched_enq())
        self.env.process(self.sched_deq())

    def sched_enq(self):
        while True:
            (head_seg_ptr, meta_ptr, tuser) = yield self.ptr_out_pipe.get()
            #self.ptr_list.append((head_seg_ptr, meta_ptr, tuser))
            print ('@ {:.2f} - Enqueue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
            pkt_des = Packet_descriptior(head_seg_ptr, meta_ptr, tuser)
            print ('@ {} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
            self.enq_pipe_cmd.put(pkt_des)
            yield self.enq_pipe_sts.get()

            #for pkt_des in pkt_list:
            (head_seg_ptr, meta_ptr, tuser) = yield self.ptr_out_pipe.get()
            print ('@ {:.2f} - Enqueue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
            pkt_des = Packet_descriptior(head_seg_ptr, meta_ptr, tuser)
            #print ('@ {} - pushed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
            self.enq_pipe_cmd.put(pkt_des)
            (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts.get()
            if popped_pkt_valid:
                self.enq_pipe_cmd.put(popped_pkt) # this poped packet should not pop another pkt in pifo (it should go into fifo)

    def sched_deq(self):
        while True:
            # wait for 10 cycles
            #for j in range(10):
            yield self.wait_sys_clks(1)

            if self.level.get_pkt_cnt() > 0:
                if self.level.pifo.get_size():
                    self.deq_pipe_req.put(-1)
                    (pkt_des, if_reload) = yield self.deq_pipe_dat.get()
                    print ('@ {} - From pifo , dequed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
                    if if_reload:
                        print('Need reload here')
                        current_fifo_index = self.level.get_cur_fifo()
                        self.find_earliest_fifo_pipe_req.put(current_fifo_index)
                        reload_fifo = yield self.find_earliest_fifo_pipe_dat.get()
                        pkt_num = self.level.fifos[reload_fifo].get_len()
                        self.reload_cmd.put((reload_fifo, pkt_num))
                        # We don't need to yield here
                else:
                    current_fifo_index = self.level.get_cur_fifo()
                    self.find_earliest_fifo_pipe_req.put(current_fifo_index)
                    deque_fifo = yield self.find_earliest_fifo_pipe_dat.get()
                    self.deq_pipe_req.put(deque_fifo)
                    (pkt_des, if_reload) = yield self.deq_pipe_dat.get()
                    print ('@ {} - From fifo {}, dequed pkt {} with rank = {}'.format(self.env.now, deque_fifo, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
                
                # update vc
                pkt_ft = pkt_des.get_finish_time(0) # TODO: do we need this debug?
                self.level.update_vc(pkt_ft)
                
                head_seg_ptr = pkt_des.get_hdr_addr()
                meta_ptr = pkt_des.get_meta_addr()
                tuser = pkt_des.get_tuser()

                print ('@ {:.2f} - Dequeue: head_seg_ptr = {} , meta_ptr = {}, tuser = {}'.format(self.env.now, head_seg_ptr, meta_ptr, tuser))
                # submit read request
                self.ptr_in_pipe.put((head_seg_ptr, meta_ptr))    


            
    
    def sched_reload(self):
        while True:
            (reload_fifo, pkt_num) = yield self.reload_cmd.get()
            print ('start to reload pifo from fifo {} with {} pkts'.format(reload_fifo, pkt_num))
            for i in range(pkt_num):
                self.deq_pipe_req.put(reload_fifo)
                (pkt_des, if_reload) = yield self.deq_pipe_dat.get()
                self.enq_pipe_cmd.put(pkt_des)
                yield self.enq_pipe_sts.get()
            self.reload_sts.put("done reloading")
