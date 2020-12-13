
class GearboxII(HW_sim_object):
    # Public
	def __init__(self, env, line_clk_period, sys_clk_period, \
        gb_enq_pipe_cmd, gb_enq_pipe_sts, gb_deq_pipe_req, gb_deq_pipe_dat, \
        granularity_list, fifo_num_list, fifo_size_list, pifo_thresh_list, pifo_size_list, \
        fifo_check_latency=1, initial_vc=0):
        super(Level, self).__init__(env, line_clk_period, sys_clk_period)

        self.granularity_list = granularity_list
        self.fifo_num_list = fifo_num_list
        self.fifo_size_list = fifo_size_list
        self.pifo_thresh_list = pifo_thresh_list
        self.pifo_size_list = pifo_size_list
        self.fifo_check_latency = fifo_check_latency

        # Gearbox enque/deque pipes
        self.gb_enq_pipe_cmd = gb_enq_pipe_cmd
        self.gb_enq_pipe_sts = gb_enq_pipe_sts
        self.gb_deq_pipe_req = gb_deq_pipe_req
        self.gb_deq_pipe_dat = gb_deq_pipe_dat

        self.migrate_data_pipe = simpy.Store(env)
        self.migrate_feedback_pipe = simpy.Store(env)


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

        # level function input/output pipes
        self.enq_pipe_cmd_arr = [] 
        self.enq_pipe_sts_arr = []
        self.deq_pipe_req_arr = []
        self.deq_pipe_dat_arr = []
        self.find_earliest_fifo_pipe_req_arr = [] 
        self.find_earliest_fifo_pipe_dat_arr = []

        self.reload_signal_arr = [] # reload_signal
        self.reload_signal_arr.append(0)

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

        enq_pipe_cmd = simpy.Store(env)
        enq_pipe_sts = simpy.Store(env)
        deq_pipe_req = simpy.Store(env)
        deq_pipe_dat = simpy.Store(env)
        find_earliest_fifo_pipe_req = simpy.Store(env)
        find_earliest_fifo_pipe_dat = simpy.Store(env)

        self.enq_pipe_cmd_arr.append(enq_pipe_cmd)
        self.enq_pipe_sts_arr.append(enq_pipe_sts)
        self.deq_pipe_req_arr.append(deq_pipe_req)
        self.deq_pipe_dat_arr.append(deq_pipe_dat)
        self.find_earliest_fifo_pipe_req_arr.append(find_earliest_fifo_pipe_req)
        self.find_earliest_fifo_pipe_dat_arr.append(find_earliest_fifo_pipe_dat)

        level0 = Base_level(env, line_clk_period, sys_clk_period, self.granularity_list[0], self.fifo_size_list[0], \
        self.enq_pipe_cmd_arr[0], self.enq_pipe_sts_arr[0], self.deq_pipe_req_arr[0], self.deq_pipe_dat_arr[0], \
        self.find_earliest_fifo_pipe_req_arr[0], self.find_earliest_fifo_pipe_dat_arr[0], \
        self.fifo_r_in_pipe_matrix[0], self.fifo_r_out_pipe_matrix[0], self.fifo_w_in_pipe_matrix[0], self.fifo_w_out_pipe_matrix[0], \
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

            enq_pipe_cmd = simpy.Store(env)
            enq_pipe_sts = simpy.Store(env)
            deq_pipe_req = simpy.Store(env)
            deq_pipe_dat = simpy.Store(env)
            find_earliest_fifo_pipe_req = simpy.Store(env)
            find_earliest_fifo_pipe_dat = simpy.Store(env)

            self.enq_pipe_cmd_arr.append(enq_pipe_cmd)
            self.enq_pipe_sts_arr.append(enq_pipe_sts)
            self.deq_pipe_req_arr.append(deq_pipe_req)
            self.deq_pipe_dat_arr.append(deq_pipe_dat)
            self.find_earliest_fifo_pipe_req_arr.append(find_earliest_fifo_pipe_req)
            self.find_earliest_fifo_pipe_dat_arr.append(find_earliest_fifo_pipe_dat)

            cur_level = Level(env, line_clk_period, sys_clk_period, self.granularity_list[index], self.fifo_size_list[index], \
            self.pifo_thresh_list[index], self.pifo_size_list[index], \
            self.enq_pipe_cmd_arr[index], self.enq_pipe_sts_arr[index], self.deq_pipe_req_arr[index], self.deq_pipe_dat_arr[index], \
            self.find_earliest_fifo_pipe_req_arr[index], self.find_earliest_fifo_pipe_dat_arr[index], \
            self.migrate_data_pipe, self.migrate_feedback_pipe, \
            self.fifo_r_in_pipe_matrix[index], self.fifo_r_out_pipe_matrix[index], \
            self.fifo_w_in_pipe_matrix[index], self.fifo_w_out_pipe_matrix[index], \
            self.pifo_r_in_pipe_arr[index], self.pifo_r_out_pipe_arr[index], \
            self.pifo_w_in_pipe_arr[index], self.pifo_w_out_pipe_arr[index], \
            fifo_write_latency=1, fifo_read_latency=1, fifo_check_latency=1, fifo_num=10, pifo_write_latency=1, pifo_read_latency=1, initial_vc=0)

            self.levels.append(cur_level)

            reload_signal_arr.append(simpy.Store(env)) # reload signal of this level
            
            index = index + 1
        
        # initiate vc
        self.virtrul_clock = initial_vc

        self.run()
    
    def run(self):
        self.env.process(self.enqueue_p())
        self.env.process(self.dequeue_p())
        #self.env.process(self.find_earliest_non_empty_fifo_p())
    
    def enque_p(self):
        while True:
            pkt = yield self.gb_enq_pipe_cmd.get() 
            pkt_finish_time = pkt.get_finish_time()

            # find the correct level to enque
            index = 0
            while (index < self.level_num):
                level_max_vc = math.floor(self.vc/self.granularity_list[index]) + self.granularity_list[index] * self.fifo_num_list[index]
                if pkt_finish_time < level_max_vc:
                    self.enq_pipe_cmd_arr[index].put(pkt_des)
                    (popped_pkt_valid, popped_pkt) = yield self.enq_pipe_sts_arr[index].get()               
                    if popped_pkt_valid:
                        self.enq_pipe_cmd_arr[index].put(popped_pkt) # this poped packet should not pop another pkt in pifo (it should go into fifo)               
                    #return
                    self.gb_enq_pipe_sts.put(1) # enque successfully
                    break
                index = index + 1
            self.gb_enq_pipe_sts.put(0) # pkt overflow
            #return


    def deque_p(self):
        while True:
            yield self.gb_deq_pipe_req.get()
            # find mininal time stamp among all levels
            #min_time_stamp = self.levels[0].get_earliest_pkt_timestamp()
            min_time_stamp = self.find_earliest_pkt_timestamp(0)
            deque_level = 0
            index = 1
            while (index < self.level_num):
                #cur_level_min_ts = self.levels[index].get_earliest_pkt_timestamp()
                cur_level_min_ts = self.find_earliest_pkt_timestamp(index)
                if cur_level_min_ts < min_time_stamp:
                    min_time_stamp = cur_level_min_ts
                    deque_level = index 
                index = index + 1
        
            # deque such packet
            if deque_level == 0:
                deque_fifo = self.get_earliest_non_empty_fifo(0)
                self.deq_pipe_req_arr[deque_level].put(deque_fifo)
                (pkt_des, if_reload) = yield self.deq_pipe_dat_arr[deque_level].get()
                self.gb_deq_pipe_dat.put(pkt_des)
                self.update_vc(pkt_des.get_finish_time()) # update vc
            else:
                if self.levels[deque_level].get_pkt_cnt() > 0:
                    if self.levels[deque_level].pifo.get_size():
                        self.deq_pipe_req_arr[deque_level].put(-1)
                        (pkt_des, if_reload) = yield self.deq_pipe_dat.get()
                        self.gb_deq_pipe_dat.put(pkt_des) # return (pkt, is_reload)
                        self.update_vc(pkt_des.get_finish_time()) # update vc
                        #print ('@ {} - From pifo , dequed pkt {} with rank = {}'.format(self.env.now, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
                        if if_reload:
                            #print('Need reload here')
                            reload_fifo = self.get_earliest_non_empty_fifo(deque_level)
                            pkt_num = self.levels[deque_level].fifos[reload_fifo].get_len()
                            #self.reload_cmd.put((reload_fifo, pkt_num)) # TODO: we need reload here
                            # We don't need to yield here
                    else:
                        deque_fifo = self.get_earliest_non_empty_fifo(deque_level)
                        self.deq_pipe_req_arr[deque_level].put(deque_fifo)
                        (pkt_des, if_reload) = yield self.deq_pipe_dat_arr[deque_level].get()
                        #print ('@ {} - From fifo {}, dequed pkt {} with rank = {}'.format(self.env.now, deque_fifo, pkt_des.get_uid(), pkt_des.get_finish_time(debug=True)))
                        self.gb_deq_pipe_dat.put(pkt_des) # return (pkt, is_reload)
                        self.update_vc(pkt_des.get_finish_time()) # update vc


    '''def sched_reload(self):
        while True:
            (reload_level, reload_fifo, pkt_num) = yield self.reload_cmd.get()
            print ('start to reload pifo from fifo {} with {} pkts'.format(reload_fifo, pkt_num))
            for i in range(pkt_num):
                self.deq_pipe_req.put(reload_fifo)
                (pkt_des, if_reload) = yield self.deq_pipe_dat.get()
                self.enq_pipe_cmd.put(pkt_des)
                yield self.enq_pipe_sts.get()
            self.reload_sts.put("done reloading")'''


    '''def migrate(self, level_index): # wait for vc update
        cur_level = self.levels[level_index]
        while(cur_level.fifos[cur_fifo].get_len()):
            pkt = cur_level.deque_fifo(cur_fifo)
            self.enque(pkt)
    # need a in pipe for the signal'''

    def migrate_p(self):
        while True:
            migrate_pkt = yield self.migrate_data_pipe.get()
            if not migrate_pkt == 0:
                self.self.gb_enq_pipe_cmd.put(migrate_pkt)
                yield self.gb_enq_pipe_sts.get()
    
    # Private

    def update_vc(vc):
        if vc > self.virtrul_clock:
            index = 0
            while (index < self.level_num):
                self.levels[index].update_vc(vc)
                if index > 0:
                    #self.env.process(self.migrate(index)) # env.provess is new thread
                    #self.migrate(index)
                    # start migrateing fifos each time when update vc
                    # TODO: is this okay for higher level to migrate each time vc is updated?
                    # TODO: how to achieve this in the back ground, start a new thread?
                index = index + 1


        return
    # Use a out pipe to send out the signal for starting migration

    # variable

    def get_earliest_non_empty_fifo(level_index):
        cur_fifo_index = self.levels[level_index].get_cur_fifo()
        self.find_earliest_fifo_pipe_req_arr[level_index].put(current_fifo_index)
        earliest_fifo = yield self.find_earliest_fifo_pipe_dat_arr[index].get()
        return earliest_fifo
    
    def find_earliest_pkt_timestamp(level_index):
        if level_index == 0:
            earliest_fifo = self.get_earliest_non_empty_fifo(0)
            earliest_pkt = self.levels.fifos[earliest_fifo].peek_front()
            return earliest_pkt.get_finish_time()
        else:
            return self.levels[level_index].get_earliest_pkt_timestamp()



    levels[]
    levels_granularity[]
    BRAM #?
    packet_storage # parse the packet into a descriptor (pkt)



