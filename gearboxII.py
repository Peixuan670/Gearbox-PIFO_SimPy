
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

            self.levels.append(cur_level)
            
            index = index + 1
        
        # initiate vc
        self.virtrul_clock = initial_vc
        return
    
    def enque(self, pkt):
        pkt_finish_time = pkt.get_finish_time()

        # find the correct level to enque
        index = 0
        while (index < self.level_num):
            level_max_vc = math.floor(self.vc/self.granularity_list[index]) + self.granularity_list[index] * self.fifo_num_list[index]
            if pkt_finish_time < level_max_vc:
                self.levels[index].enque(pkt)
                return
            index = index + 1
        return


    def deque(self):
        # find mininal time stamp among all levels
        min_time_stamp = self.levels[0].get_earliest_pkt_timestamp()
        deque_level = 0
        index = 1
        while (index < self.level_num):
            cur_level_min_ts = self.levels[index].get_earliest_pkt_timestamp()
            if cur_level_min_ts < min_time_stamp:
                min_time_stamp = cur_level_min_ts
                deque_level = index 
            index = index + 1
        
        # deque such packet
        if deque_level == 0:
            return self.levels[0].deque_earliest_pkt()
        else:
            return self.levels[index].deque_pifo()




    def migrate(self, level):

    # Private

    def update_vc(vc):
        if vc > self.virtrul_clock:
            index = 0
            while (index < self.level_num):
                self.levels[index].update_vc(vc)
                index = index + 1
        return

    # variable



    levels[]
    levels_granularity[]
    BRAM #?
    packet_storage # parse the packet into a descriptor (pkt)



