import math

# Peixuan 11122020
# This is the base level (level 0), no pifo
class BaseLevel(HW_sim_object):
	# Public
    def __init__(self, env, period, granularity, fifo_size, fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, \
        fifo_w_in_pipe_arr, fifo_w_out_pipe_arr, fifo_write_latency=1, fifo_read_latency=1, \
        fifo_check_latency=1, fifo_num=10, initial_vc=0):
        super(BaseLevel, self).__init__(env, period)
        self.granularity = granularity
        self.fifo_num = fifo_num
        self.fifo_size = fifo_size

        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency


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


        
        

    # Private

    # Methods

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
        fifo_index_offset = math.floor(pkt.getFinishTime() / self.granularity) - math.floor(self.vc / self.granularity)
        # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
        enque_fifo_index = (self.cur_fifo + fifo_index_offset) % self.fifo_num
        self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
        return

    	

    def deque_fifo(self, fifo_index):
    	# deque packet from sepecific fifo, when migrating packets
        self.fifo_r_in_pipe_arr[fifo_index].put(1) 
        dequed_pkt = yield self.fifo_r_out_pipe_arr[fifo_index].get()
        return dequed_pkt

    def get_earliest_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        if self.fifos[self.cur_fifo].get_len():
            top_pkt = self.fifos[self.cur_fifo].peek_front()
            return top_pkt.getFinishTime()
        else:
            earliest_fifo = self.find_next_non_empty_fifo(self.cur_fifo)
            if earliest_fifo > -1:
                top_pkt = self.fifos[earliest_fifo].peek_front()
                return top_pkt.getFinishTime()
            else:
                return -1 # there is no pkt in this level

    def update_vc(self, vc):
        # Update vc
        if self.vc < vc:
            self.vc = vc
        # update current serving fifo
        if self.fifos[self.cur_fifo].get_len() is 0:
            self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num       
        return self.vc

    # Tuser + headpointer as pkt
