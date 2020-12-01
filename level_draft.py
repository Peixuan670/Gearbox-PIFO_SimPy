import math
from hwsim_utils import *
from packet import Packet_descriptior
from queues import FIFO, PIFO

# Peixuan 11042020
class Level(HW_sim_object):
	# Public
    def __init__(self, env, line_clk_period, sys_clk_period, granularity, fifo_size, pifo_thresh, pifo_size, \
        enq_pipe_cmd, enq_pipe_sts, deq_pipe_req, deq_pipe_dat, \
        find_earliest_fifo_pipe_req, find_earliest_fifo_pipe_dat, \
        fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, fifo_w_in_pipe_arr, fifo_w_out_pipe_arr,\
        pifo_r_in_pipe, pifo_r_out_pipe, pifo_w_in_pipe, pifo_w_out_pipe,\
        fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, \
        pifo_write_latency=1, pifo_read_latency=1, initial_vc=0):
        super(Level, self).__init__(env, line_clk_period, sys_clk_period)
        self.granularity = granularity
        self.fifo_num = fifo_num
        self.fifo_size = fifo_size
        self.pifo_thresh = pifo_thresh
        self.pifo_size = pifo_size

        self.enq_pipe_cmd = enq_pipe_cmd
        self.enq_pipe_sts = enq_pipe_sts
        self.deq_pipe_req = deq_pipe_req
        self.deq_pipe_dat = deq_pipe_dat
        self.find_earliest_fifo_pipe_req = find_earliest_fifo_pipe_req
        self.find_earliest_fifo_pipe_dat = find_earliest_fifo_pipe_dat

        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency

        self.pifo_read_latency = pifo_read_latency
        self.pifo_write_latency = pifo_write_latency

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
            
            new_fifo = FIFO(env, line_clk_period, sys_clk_period, self.fifo_r_in_pipe_arr[index], self.fifo_r_out_pipe_arr[index], \
                self.fifo_w_in_pipe_arr[index], self.fifo_w_out_pipe_arr[index], maxsize=self.fifo_size, \
                    write_latency=self.fifo_write_latency, read_latency=self.fifo_read_latency, init_items=[])
            self.fifos.append(new_fifo) 

            index = index + 1

        # Initialize PIFO

        self.pifo_r_in_pipe = pifo_r_in_pipe
        self.pifo_r_out_pipe = pifo_r_out_pipe
        self.pifo_w_in_pipe = pifo_w_in_pipe
        self.pifo_w_out_pipe = pifo_w_out_pipe

        self.pifo = PIFO(env, line_clk_period, sys_clk_period, self.pifo_r_in_pipe, self.pifo_r_out_pipe, self.pifo_w_in_pipe, \
            self.pifo_w_out_pipe, maxsize=self.pifo_size, write_latency=self.pifo_write_latency, read_latency=self.pifo_read_latency, init_items=[])


        
        

    # Private

    '''# var:
    fifos[]		# FIFO instances array
    fifos_r_in_pipe_arr[]  # fifo read handle array
    fifos_w_in_pipe_arr[]  # fifo write handle array

    pifo 		# PIFO instance (or two?)

    fifo_num	# total number of FIFOs
    fifo_size	# size of each FIFO
    pifo_thresh # (reload) threshold of the PIFO
    pifo_size	# size of the PIFO
    #?pifo_num	# TODO ?

    cur_vc		# current vritual clock
    cur_fifo	# current serving fifo

    max_ts_pifo # max time stamp in pifo'''

    # Methods

    def reload(self, fifo_index, pkt_num):
    	# reload the pifo
    	# traverse the first non-empty fifo next to the current serving fifo and put into the pifo
        traversed_pkt = 0
        while (traversed_pkt < pkt_num):
            traversed_pkt = traversed_pkt+1
            cur_pkt = self.deque_fifo(fifo_index)

            # enque pifo
            self.pifo_w_in_pipe.put(cur_pkt) 
            ((done, popped_pkt, popped_pkt_valid)) = yield self.pifo_w_out_pipe.get() # tuple
            if popped_pkt_valid:
                # recycle the popped pkt from pifo
                self.enque(popped_pkt)


    	# for pkts kicked out from pifo, put back the the fifo it belongs to (call enque(pkt))


    # Public

    def find_earliest_non_empty_fifo_p(self):        
        while True:
            index = yield self.find_earliest_fifo_pipe_req.get() # fifo index, find the earliest non-empty fifo from this fifo
            print ('Check earliest fifo from index {}'.format(index))
            yield self.wait_sys_clks(self.fifo_check_latency)
            cur_index = index            
            while True:
                if not self.fifos[cur_index].get_len() == 0:
                    self.find_earliest_fifo_pipe_dat.put(cur_index)
                    print ('Found earliest fifo{}'.format(cur_index))
                    break
                cur_index = cur_index + 1
                if (cur_index == self.fifo_num):
                    # recirculate if go to the back of the level
                    cur_index = 0
                if (cur_index == index):
                    self.find_earliest_fifo_pipe_dat.put(-1) # this means all the fifos are empty
                    print ('All fifos are empty')
                    break

    
    def enqueue_p(self):
#    def enque(self, pkt):
        while True:
            pkt = yield self.enq_pipe_cmd.get() 
            if not pkt == 0:
                if pkt.get_finish_time() < self.get_pifo_max_pkt_timestamp():
                    # If new pkt's finish time < max time stamp in pifo, enque pifo
                    self.pifo_w_in_pipe.put(pkt)
                    ((done, popped_pkt, popped_pkt_valid)) = yield self.pifo_w_out_pipe.get() # tuple
                    if popped_pkt_valid:
                        # recycle the popped pkt from pifo, send the packet out # TODO: can we directly send it back to enque pipe?
                        self.enq_pipe_sts.put((popped_pkt_valid, popped_pkt))
                        #break # TODO: break to where
                    else:
                        self.enq_pipe_sts.put((popped_pkt_valid, 0))
                else:
                    # read the pkt's finish time and find correct fifo to enque
                    fifo_index_offset = math.floor(pkt.getFinishTime() / self.granularity) - math.floor(self.vc / self.granularity)
                    # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
                    enque_fifo_index = (self.cur_fifo + fifo_index_offset) % self.fifo_num
                    self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
                    yield self.fifo_w_out_pipe_arr[enque_fifo_index].get()
                    self.enq_pipe_sts.put((0, 0))
                # return ((popped_pkt_valid, popped_pkt)), if enque fifo, return (0, 0)
            else:
                print("Illegal packet")
    

    def dequeue_p(self):
        # request includes queue index to deque:
        # queue_index = -1: PIFO
        # queue_index >= 0: FIFO
        while True:
            index = yield self.deq_pipe_req.get()
            if index == -1: 
                # deque PIFO
                self.pifo_r_in_pipe.put(1)
                dequed_pkt = yield self.pifo_r_out_pipe.get()
                if self.pifo.get_occupancy() < self.pifo_thresh: 
                    # if pifo.len < pifo_thresh, reload pifo
                    reload_fifo = self.find_next_non_empty_fifo(self.cur_fifo) # get next non-empty fifo as reload fifo
                    pkt_num = len(self.fifos[reload_fifo].items)
                    self.deq_pipe_dat.put((dequed_pkt, 1, reload_fifo, pkt_num)) # return (pkt, is_reload, reload_fifo, pkt_num)
                    print("Need to reload PIFO")
            else: 
                # deque FIFO[index]
                if self.deq_pipe_dat is not None:
                    self.fifo_r_in_pipe_arr[index].put(1)
                    dequed_pkt = yield self.fifo_r_out_pipe_arr[index].get()
                    self.deq_pipe_dat.put((dequed_pkt, 0, 0, 0))

    def get_earliest_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        top_pkt = self.pifo.peek_front()
        return top_pkt.get_finish_time()
    
    def get_pifo_max_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        tail_pkt = self.pifo.peek_tail()
        return tail_pkt.getFinishTime()

    def update_vc(self, vc):
        # Update vc
        if self.vc < vc:
            self.vc = vc
        # update current serving fifo
        if self.fifos[self.cur_fifo].get_len() is 0:
            self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num       
        return self.vc

    # Tuser + headpointer as pkt
