import math

# Peixuan 11042020
class Level(HW_sim_object):
	# Public
    def __init__(self, env, period, granularity, fifo_size, pifo_thresh, pifo_size, \
        fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, fifo_w_in_pipe_arr, fifo_w_out_pipe_arr,\
        pifo_r_in_pipe, pifo_r_out_pipe, pifo_w_in_pipe, pifo_w_out_pipe,\
        fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, \
        pifo_write_latency=1, pifo_read_latency=1, initial_vc=0):
        super(Level, self).__init__(env, period)
        self.granularity = granularity
        self.fifo_num = fifo_num
        self.fifo_size = fifo_size
        self.pifo_thresh = pifo_thresh
        self.pifo_size = pifo_size

        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency

        self.pifo_read_latency = pifo_read_latency
        self.pifo_write_latency = pifo_write_latency

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
            
            new_fifo = FIFO(env, period, self.fifo_r_in_pipe_arr[index], self.fifo_r_out_pipe_arr[index], \
                self.fifo_w_in_pipe_arr[index], self.fifo_w_out_pipe_arr[index], maxsize=self.fifo_size, \
                    write_latency=self.fifo_write_latency, read_latency=self.fifo_read_latency, init_items=[])
            self.fifos.append(new_fifo) 

            index = index + 1

        # Initialize PIFO

        self.pifo_r_in_pipe = pifo_r_in_pipe
        self.pifo_r_out_pipe = pifo_r_out_pipe
        self.pifo_w_in_pipe = pifo_w_in_pipe
        self.pifo_w_out_pipe = pifo_w_out_pipe

        self.pifo = PIFO(env, period, self.pifo_r_in_pipe, self.pifo_r_out_pipe, self.pifo_w_in_pipe, \
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

    def find_next_non_empty_fifo(self, index):
    	# find the next non-empty fifo next to fifo[index]
        # model check latency
        for i in range(self.fifo_check_latency):
            yield self.wait_clock()
        
        cur_fifo_index = index
        while ():
            cur_fifo_index = cur_fifo_index + 1
            if (cur_fifo_index is self.fifo_num):
                # recirculate if go to the back of the level
                cur_fifo_index = 0

            if (cur_fifo_index is index):
                return -1 # this means all the fifos are empty
            else:
                if self.fifos[cur_fifo_index].get_len(): # TODO can I do this here? Non-zero as true?
                    return cur_fifo_index
        return


    # Public

    

    def enque(self, pkt):
        # TODO: what is such pkt, we only deal with the discriptor
        if pkt.getFinishTime() < self.get_pifo_max_pkt_timestamp():
            # If new pkt's finish time < max time stamp in pifo, enque pifo
            self.pifo_w_in_pipe.put(pkt)
            ((done, popped_pkt, popped_pkt_valid)) = yield self.pifo_w_out_pipe.get() # tuple
            if popped_pkt_valid:
                # recycle the popped pkt from pifo
                self.enque(popped_pkt)
            return
        else:
    	    # read the pkt's finish time and find correct fifo to enque
            fifo_index_offset = math.floor(pkt.getFinishTime() / self.granularity) - math.floor(self.vc / self.granularity)
            # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
            enque_fifo_index = (self.cur_fifo + fifo_index_offset) % self.fifo_num
            self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
            return


    def deque_pifo(self):
    	# when a pkt need to leave directly from this level, use deque pifo (earliest pkt)
        self.pifo_r_in_pipe.put(1) 
        dequed_pkt = yield self.pifo_r_out_pipe.get()
        if self.pifo.get_occupancy() < self.pifo_thresh: 
            # if pifo.len < pifo_thresh, reload pifo
            reload_fifo = self.find_next_non_empty_fifo(self.cur_fifo) # get next non-empty fifo as reload fifo
            pkt_num = len(self.fifos[reload_fifo].items)
            self.reload(reload_fifo, pkt_num)
        return dequed_pkt

    	

    def deque_fifo(self, fifo_index):
    	# deque packet from sepecific fifo, when migrating packets
        self.fifo_r_in_pipe_arr[fifo_index].put(1) 
        dequed_pkt = yield self.fifo_r_out_pipe_arr[fifo_index].get()
        return dequed_pkt

    def get_earliest_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        top_pkt = self.pifo.peek_front()
        return top_pkt.getFinishTime()
    
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
