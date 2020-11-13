
class GearboxII(HW_sim_object):
    # Public
	def __init__(self, env, period, granularity_list, fifo_num_list, fifo_size_list, pifo_thresh_list, pifo_size_list, fifo_check_latency=1, initial_vc=0):
        super(Level, self).__init__(env, period)

        self.granularity_list = granularity_list
        self.fifo_num_list = fifo_num_list
        self.fifo_size_list = fifo_size_list
        self.pifo_thresh_list = pifo_thresh_list
        self.pifo_size_list = pifo_size_list
        self.fifo_check_latency = fifo_check_latency


        # Initiate all the levels
        index = 1
        while (index < self.level_num):
            self.fifo_r_in_pipe_arr.append(simpy.Store(env))
            self.fifo_r_out_pipe_arr.append(simpy.Store(env))
            self.fifo_w_in_pipe_arr.append(simpy.Store(env))
            self.fifo_w_out_pipe_arr.append(simpy.Store(env))
            
            new_fifo = FIFO(env, period, self.fifo_r_in_pipe_arr[index], self.fifo_r_out_pipe_arr[index], self.fifo_w_in_pipe_arr[index], self.fifo_w_out_pipe_arr[index], maxsize=self.fifo_size, write_latency=1, read_latency=2, init_items=[])
            self.fifos.append(new_fifo) 

            index = index + 1
    
    def enque(self, pkt):


    def deque(self):

    def migrate(self, level):

    # Private

    # variable

    levels[]
    levels_granularity[]
    BRAM #?
    packet_storage # parse the packet into a descriptor (pkt)



