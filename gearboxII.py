
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
        self.levels = []

        self.fifo_r_in_pipe_matrix = [][]
        self.fifo_r_out_pipe_matrix = [][]
        self.fifo_w_in_pipe_matrix = [][]
        self.fifo_w_out_pipe_matrix = [][]

        self.pifo_r_in_pipe_arr = []
        self.pifo_r_out_pipe_arr = []
        self.pifo_w_in_pipe_arr = []
        self.pifo_w_out_pipe_arr = []

        # initiate level 0

        fifo_r_in_pipe_arr = []
        fifo_r_out_pipe_arr = []
        fifo_w_in_pipe_arr = []
        fifo_w_out_pipe_arr = []

        while (index < self.fifo_num_list[0]):
            fifo_r_in_pipe_arr.append(simpy.Store(env))
            fifo_r_out_pipe_arr.append(simpy.Store(env))
            fifo_w_in_pipe_arr.append(simpy.Store(env))
            fifo_w_out_pipe_arr.append(simpy.Store(env))
        
        self.fifo_r_in_pipe_matrix.append(fifo_r_in_pipe_arr)
        self.fifo_r_out_pipe_matrix.append(fifo_r_out_pipe_arr)
        self.fifo_w_in_pipe_matrix.append(fifo_w_in_pipe_arr)
        self.fifo_w_out_pipe_matrix.append(fifo_w_out_pipe_arr)

        level0 = Base_level(env, period, self.granularity_list[0], self.fifo_size_list[0], self.fifo_r_in_pipe_matrix[0], \
        self.fifo_r_out_pipe_matrix[0], self.fifo_w_in_pipe_matrix[0], self.fifo_w_out_pipe_matrix[0], \
        fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, initial_vc=0)
        self.levels.append(level0)


        index = 1
        while (index < self.level_num):

            fifo_r_in_pipe_arr = []
            fifo_r_out_pipe_arr = []
            fifo_w_in_pipe_arr = []
            fifo_w_out_pipe_arr = []

            while (index < self.fifo_num_list[index]):
                fifo_r_in_pipe_arr.append(simpy.Store(env))
                fifo_r_out_pipe_arr.append(simpy.Store(env))
                fifo_w_in_pipe_arr.append(simpy.Store(env))
                fifo_w_out_pipe_arr.append(simpy.Store(env))

            self.fifo_r_in_pipe_matrix.append(fifo_r_in_pipe_arr)
            self.fifo_r_out_pipe_matrix.append(fifo_r_out_pipe_arr)
            self.fifo_w_in_pipe_matrix.append(fifo_w_in_pipe_arr)
            self.fifo_w_out_pipe_matrix.append(fifo_w_out_pipe_arr)

            self.pifo_r_in_pipe_arr.append(simpy.Store(env))
            self.pifo_r_out_pipe_arr.append(simpy.Store(env))
            self.pifo_w_in_pipe_arr.append(simpy.Store(env))
            self.pifo_w_out_pipe_arr.append(simpy.Store(env))

            cur_level = Level(env, period, self.granularity_list[index], self.fifo_size_list[index], self.pifo_thresh_list[index], \
            self.pifo_size_list[index], self.fifo_r_in_pipe_matrix[index], self.fifo_r_out_pipe_matrix[index], \
            self.fifo_w_in_pipe_matrix[index], self.fifo_w_out_pipe_matrix[index],self.pifo_r_in_pipe_arr[index], \
            self.pifo_r_out_pipe_arr[index], self.pifo_w_in_pipe_arr[index], self.pifo_w_out_pipe_arr[index], \
            fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, pifo_write_latency=1, pifo_read_latency=1, initial_vc=0)
            
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



