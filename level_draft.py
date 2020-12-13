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
        #reload_req, reload_sts, \
        #migrate_signal, \
        migrate_data_pipe, migrate_feedback_pipe, \
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

        self.migrate_signal = simpy.Store(env)
        self.migrate_data_pipe = migrate_data_pipe
        self.migrate_feedback_pipe = migrate_feedback_pipe

        self.fifo_read_latency = fifo_read_latency
        self.fifo_write_latency = fifo_write_latency
        self.fifo_check_latency = fifo_check_latency

        self.pifo_read_latency = pifo_read_latency
        self.pifo_write_latency = pifo_write_latency

        self.fifos = []

        self.reload_req = simpy.Store(env)
        self.reload_sts = simpy.Store(env)
        #self.reload_req = reload_req
        #self.reload_sts = reload_sts

        # Initialize pkt cnt
        self.pkt_cnt = 0

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

        self.recycle_cnt = 0 # debug
        self.reload_recycle_cnt = 0 # debug

        self.run()

        

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

    '''def reload(self, fifo_index, pkt_num):
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


    	# for pkts kicked out from pifo, put back the the fifo it belongs to (call enque(pkt))'''
    
    def run(self):
        self.env.process(self.enqueue_p())
        self.env.process(self.dequeue_p())
        self.env.process(self.reload_p())
        self.env.process(self.find_earliest_non_empty_fifo_p())


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
        while True:
            pkt = yield self.enq_pipe_cmd.get() 
            print('Start enquing')
            if not pkt == 0:
                if pkt.get_finish_time(0) < self.get_pifo_max_pkt_timestamp():
                    # If new pkt's finish time < max time stamp in pifo, enque pifo
                    self.pifo_w_in_pipe.put(pkt)
                    ((done, popped_pkt, popped_pkt_valid)) = yield self.pifo_w_out_pipe.get() # tuple
                    self.pkt_cnt = self.pkt_cnt + 1 # pkt cnt ++
                    print('Enqued PIFO, pkt_cnt = {}'.format(self.pkt_cnt))
                    if popped_pkt_valid:
                        self.pkt_cnt = self.pkt_cnt - 1 # poped pkt
                        self.recycle_cnt = self.recycle_cnt + 1 # debug
                        print('Recycle pkt: {}'.format(self.recycle_cnt))
                        
                        # recycle the popped pkt from pifo, send the packet out # TODO: can we directly send it back to enque pipe?
                        self.enq_pipe_sts.put((popped_pkt_valid, popped_pkt))
                        #break # TODO: break to where
                    else:
                        self.enq_pipe_sts.put((popped_pkt_valid, 0))
                else:
                    # read the pkt's finish time and find correct fifo to enque
                    fifo_index_offset = math.floor(pkt.get_finish_time(0) / self.granularity) - math.floor(self.vc / self.granularity)
                    #print('pkt ft = {}'.format(pkt.get_finish_time(0))) # debug
                    #print('Gran = {}'.format(self.granularity))    # debug
                    #print('pkt.get_finish_time(0) / self.granularity = {}'.format(pkt.get_finish_time(0) / self.granularity)) # debug
                    #print('self.vc / self.granularity = {}'.format(self.vc / self.granularity)) # debug
                    # we need to first use the granularity to round up vc and pkt.finish_time to calculate the fifo offset
                    enque_fifo_index = (self.cur_fifo + fifo_index_offset) % self.fifo_num
                    self.fifo_w_in_pipe_arr[enque_fifo_index].put(pkt)
                    yield self.fifo_w_out_pipe_arr[enque_fifo_index].get()
                    self.pkt_cnt = self.pkt_cnt + 1 # pkt cnt ++
                    print('Enqued FIFO vc + {}, pkt_cnt = {}'.format(fifo_index_offset, self.pkt_cnt))
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
                self.pkt_cnt = self.pkt_cnt - 1 # pkt cnt --
                print('Dequed PIFO, pkt_cnt = {}'.format(self.pkt_cnt))
                if self.pifo.get_size() < self.pifo_thresh: 
                    self.deq_pipe_dat.put((dequed_pkt, 1)) # return (pkt, is_reload)
                    self.reload_req.put(1) # initial reload
                    ##print("Need to reload PIFO")
                else:
                    self.deq_pipe_dat.put((dequed_pkt, 0)) # return (pkt, is_reload)
            else: 
                # deque FIFO[index]
                if self.deq_pipe_dat is not None:
                    self.fifo_r_in_pipe_arr[index].put(1)
                    dequed_pkt = yield self.fifo_r_out_pipe_arr[index].get()
                    self.deq_pipe_dat.put((dequed_pkt, 0))
                    self.pkt_cnt = self.pkt_cnt - 1 # pkt cnt --
                    print('Dequed FIFO {}, pkt_cnt = {}'.format(index, self.pkt_cnt))

    def reload_p(self):
        while True:
            yield self.reload_req.get()
            print("@@@@@@ reload function here")
            print("@@@When reload, current pifo size: {}".format(self.pifo.get_size()))
            self.find_earliest_fifo_pipe_req.put(self.cur_fifo)
            fifo_index = yield self.find_earliest_fifo_pipe_dat.get()
            print('Reload from fifo {}'.format(fifo_index))
            pkt_num = self.fifos[fifo_index].get_len()
            for i in range(pkt_num):
                if not self.fifos[fifo_index].get_len() == 0:
                    self.fifo_r_in_pipe_arr[fifo_index].put(1)
                    reload_pkt = yield self.fifo_r_out_pipe_arr[fifo_index].get()
                    print('Get pkt: {}, remain reload #{}, current fifo len: {}'.format(reload_pkt, pkt_num - i, self.fifos[fifo_index].get_len()))

                    if not reload_pkt == 0: #sanity check

                        print("***Start reload this pkt, current pifo size: {}".format(self.pifo.get_size()))
                        self.pifo_w_in_pipe.put(reload_pkt)
                        print("***Reloaded pifo with pkt: {}".format(reload_pkt))
                        ((done, popped_pkt, popped_pkt_valid)) = yield self.pifo_w_out_pipe.get() # tuple
                        print("***Finish reload this pkt, current pifo size: {}".format(self.pifo.get_size()))
                        if popped_pkt_valid:
                            self.pkt_cnt = self.pkt_cnt - 1 # pkt cnt --
                            self.reload_recycle_cnt = self.reload_recycle_cnt + 1
                            print("***** popped packet, total poped {} pkts during reload".format(self.reload_recycle_cnt))
                            # recycle the popped pkt from pifo, send the packet out # TODO: can we directly send it back to enque pipe?
                            self.enq_pipe_cmd.put(popped_pkt)
                            self.reload_sts.put((popped_pkt_valid, popped_pkt))
                        else:
                            self.reload_sts.put((popped_pkt_valid, 0))


    def migrate_p(self):
        while True:
            (fifo_index, pkt_num) = yield self.migrate_signal.get()
            for i in range(pkt_num):
                self.deq_pipe_req.put(fifo_index)
                (migrate_pkt, is_reload) = yield self.deq_pipe_dat.get()
                if not migrate_pkt == 0:
                    self.migrate_data_pipe.put(migrate_pkt)
                    yield self.migrate_feedback_pipe.get()
                    print("Migrated pkt {}".format(migrate_pkt))

    
    
    def get_earliest_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        top_pkt = self.pifo.peek_front()
        if top_pkt:
            return top_pkt.get_finish_time(0)
        else:
            return -1 # empty pifo in this level
    
    def get_pifo_max_pkt_timestamp(self):
    	# return time stamp from the head of PIFO
        if self.pifo.get_size() < self.pifo_size:
            return math.inf # if pifo is not full, then max timestamp = infinity
        else:
            tail_pkt = self.pifo.peek_tail()
            return tail_pkt.get_finish_time(0)

    def update_vc(self, vc):
        # Update vc
        prev_fifo = self.cur_fifo

        if self.vc < vc:
            self.vc = vc
        # update current serving fifo
        if self.fifos[self.cur_fifo].get_len() is 0:
            self.cur_fifo = math.floor(self.vc / self.granularity) % self.fifo_num
        if not prev_fifo == self.cur_fifo:
            # we need to migrate here
            pkt_num = self.fifos[self.cur_fifo].get_len()
            if not pkt_num == 0:
                self.migrate_signal.put(self.cur_fifo, pkt_num)
                print("Starting migrate fifo: {} with {} pkts".format(self.cur_fifo, pkt_num))       
        return self.vc

    # Tuser + headpointer as pkt

    def get_cur_fifo(self):
        return self.cur_fifo
    
    def get_pkt_cnt(self):
        return self.pkt_cnt
    
    def get_level_size(self):
        pkt_cnt = 0
        for fifo in self.fifos:
            pkt_cnt = pkt_cnt + fifo.get_len()
        
        pkt_cnt = pkt_cnt + self.pifo.get_size()
        return pkt_cnt
