import math
from hwsim_utils import *
from packet import Packet_descriptior
from queues import FIFO, PIFO

# Peixuan 11122020
# This is the base level (level 0), no pifo
class Base_level(HW_sim_object):
    # Public
    def __init__(self, env, line_clk_period, sys_clk_period, granularity, fifo_size, \
                 enq_pipe_cmd, enq_pipe_sts, deq_pipe_req, deq_pipe_dat, \
                 fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, fifo_w_in_pipe_arr, fifo_w_out_pipe_arr, \
                 fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0):
                 
        super(Base_level, self).__init__(env, line_clk_period, sys_clk_period)
        self.granularity = granularity
        self.fifo_num = fifo_num
        self.fifo_size = fifo_size
        self.enq_pipe_cmd = enq_pipe_cmd
        self.enq_pipe_sts = enq_pipe_sts
        self.deq_pipe_req = deq_pipe_req
        self.deq_pipe_dat = deq_pipe_dat
        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency

        self.fifos = []

        # Initialize VC

        self.vc = initial_vc
        self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num
        
        # Initialize FIFO array and read/write handle
        
        self.fifo_r_in_pipe_arr = fifo_r_in_pipe_arr
        self.fifo_r_out_pipe_arr = fifo_r_out_pipe_arr
        self.fifo_w_in_pipe_arr = fifo_w_in_pipe_arr
        self.fifo_w_out_pipe_arr = fifo_w_out_pipe_arr
        
        index = 0
        while (index < self.fifo_num):
            #self.fifo_r_in_pipe_arr.append(simpy.Store(env))
            #self.fifo_r_out_pipe_arr.append(simpy.Store(env))
            #self.fifo_w_in_pipe_arr.append(simpy.Store(env))
            #self.fifo_w_out_pipe_arr.append(simpy.Store(env))
            init_items = []
            
            new_fifo = FIFO(env, line_clk_period, sys_clk_period, self.fifo_r_in_pipe_arr[index], self.fifo_r_out_pipe_arr[index], \
                self.fifo_w_in_pipe_arr[index], self.fifo_w_out_pipe_arr[index], self.fifo_size, \
                    self.fifo_write_latency, self.fifo_read_latency, init_items)
            self.fifos.append(new_fifo) 

            index = index + 1
            
        self.run()

    def run(self):
        self.env.process(self.enqueue_p())
        self.env.process(self.dequeue_earliest_pkt_p())

    # Private

    # Methods

    def find_next_non_empty_fifo(self, index):
        # find the next non-empty fifo next to fifo[index]
        # ***** TODO: cannot mix return and yield statements.  if we need to model latency,
        # ***** we have to make this a generator (process) and communicate with it using pipes
        # model check latency
        #for i in range(self.fifo_check_latency):
        #    yield self.wait_clock()
        cur_fifo_index = index
        while True:
            cur_fifo_index = cur_fifo_index + 1
            if (cur_fifo_index == self.fifo_num):
                # recirculate if go to the back of the level
                cur_fifo_index = 0

            if (cur_fifo_index == index):
                return -1 # this means all the fifos are empty
            else:
                if self.fifos[cur_fifo_index].get_len(): # TODO can I do this here? Non-zero as true?
                    return cur_fifo_index
        return


    # Public


    def enqueue_p(self):
#    def enque(self, pkt):
        while True:
            pkt = yield self.enq_pipe_cmd.get() 
            if not pkt == 0:
                fifo_index_offset = math.floor(pkt.get_finish_time(debug=False) / self.granularity) - math.floor(self.vc / self.granularity)
                # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
                enque_fifo_index = (self.cur_fifo + fifo_index_offset) % self.fifo_num
                self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
                yield self.fifo_w_out_pipe_arr[enque_fifo_index].get()
                self.enq_pipe_sts.put(1)
            else:
                print("Illegal packet")

    """
    def deque_fifo(self, fifo_index):
        # deque packet from sepecific fifo, when migrating packets
        print ("deque_fifo {}".format(fifo_index))
        self.fifo_r_in_pipe_arr[fifo_index].put(1) 
        print ("requested pkt from fifo {}".format(fifo_index))
        dequed_pkt = yield self.fifo_r_out_pipe_arr[fifo_index].get()
        print ("dequeued pkt {} from fifo {}".format(dequed_pkt, fifo_index))
        return dequed_pkt
    """
    
    def get_earliest_pkt_timestamp(self):
        # return time stamp from the head of PIFO
        if self.fifos[self.cur_fifo].get_len():
            top_pkt = self.fifos[self.cur_fifo].peek_front()
            return top_pkt.get_finish_time()
        else:
            earliest_fifo = self.find_next_non_empty_fifo(self.cur_fifo)
            if earliest_fifo > -1:
                top_pkt = self.fifos[earliest_fifo].peek_front()
                return top_pkt.get_finish_time()
            else:
                return -1 # there is no pkt in this level
    
#    def deque_earliest_pkt(self):
    def dequeue_earliest_pkt_p(self):
        while True:
            yield self.deq_pipe_req.get()
            if self.fifos[self.cur_fifo].get_len():
                fifo_index = self.cur_fifo
            else:
                earliest_fifo = self.find_next_non_empty_fifo(self.cur_fifo)
                if earliest_fifo > -1:
                    fifo_index = earliest_fifo
                else:
                    #return -1 # there is no pkt in this level
                    #***** TODO: fix this - pipe should have only packets *****
                    self.deq_pipe_dat.put(-1) # there is no pkt in this level

            # request FIFO read
            self.fifo_r_in_pipe_arr[fifo_index].put(1) 
            dequed_pkt = yield self.fifo_r_out_pipe_arr[fifo_index].get()
            self.deq_pipe_dat.put(dequed_pkt)

    def update_vc(self, vc):
        # Update vc
        if self.vc < vc:
            self.vc = vc
        # update current serving fifo
        if self.fifos[self.cur_fifo].get_len() == 0:
            self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num       
        return self.vcx