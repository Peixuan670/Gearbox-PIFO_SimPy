
import sys, os
from scapy.all import *
import simpy
import math
from collections import OrderedDict

class Tuser(object):
    def __init__(self, pkt_len, src_port, dst_port, rank, pkt_id):
        self.pkt_len = pkt_len
        self.src_port = src_port
        self.dst_port = dst_port
        self.rank = rank
        self.pkt_id = pkt_id # used for stats only

    def __str__(self):
        return '{{ pkt_len: {}, src_port: {:08b}, dst_port: {:08b}, rank: {}, pkt_id: {} }}'.format(self.pkt_len, self.src_port, self.dst_port, self.rank, self.pkt_id)

class Fifo(object):
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.items = []

    def push(self, item):
        if len(self.items) < self.maxsize:
            self.items.append(item)
        else:
            print >> sys.stderr, "ERROR: attempted to write to full FIFO"

    def pop(self):
        if len(self.items) > 0:
            item = self.items[0]
            self.items = self.items[1:]
            return item
        else:
            print >> sys.stderr, "ERROR: attempted to read from empty FIFO"
            return None

    def fill_level(self):
        return (len(self.items))

    def __str__(self):
        return str(self.items)

class AXI_S_message(object):
    def __init__(self, tdata, tvalid, tkeep, tlast, tuser):
        self.tdata = tdata
        self.tvalid = tvalid
        self.tkeep = tkeep
        self.tlast = tlast
        self.tuser = tuser

    def __str__(self):
        return "{{tdata: {}, tvalid: {}, tkeep: {:08x}, tlast: {}, tuser: {} }}".format(''.join('{:02x}'.format(ord(c)) for c in self.tdata), self.tvalid, self.tkeep, self.tlast, self.tuser)

class HW_sim_object(object):
    def __init__(self, env, period):
        self.env = env
        self.period = period

    def clock(self):
        yield self.env.timeout(self.period)

    def wait_clock(self):
        return self.env.process(self.clock())

class BRAM(HW_sim_object):
    def __init__(self, env, period, r_in_pipe, r_out_pipe, w_in_pipe, w_out_pipe=None, depth=128, write_latency=1, read_latency=1):
        super(BRAM, self).__init__(env, period)
        self.r_in_pipe = r_in_pipe
        self.r_out_pipe = r_out_pipe
        self.w_in_pipe = w_in_pipe
        self.w_out_pipe = w_out_pipe
        self.rd_count = 0
        self.wr_count = 0
        self.write_latency = write_latency
        self.read_latency = read_latency
        self.depth = depth
        self.mem = OrderedDict()
        for addr in range(depth):
            self.mem[addr] = None

        # register processes for simulation
        self.run()

    def run(self):
        self.env.process(self.write_sm())
        self.env.process(self.read_sm())

    def write_sm(self):
        """
        State machine to write incomming data into memory
        """
        while True:
            # wait to receive incoming data
            (addr, data) = yield self.w_in_pipe.get()
            # model write latency
            for i in range(self.write_latency):
                yield self.wait_clock()
            # try to write data into memory
            if addr in self.mem.keys():
                self.mem[addr] = data
            else:
                print >> sys.stderr, "ERROR: BRAM write_sm: specified address {} is out of range".format(addr)
            # indicate write_completion
            self.wr_count += 1
            if self.w_out_pipe is not None:
                done = 1
                self.w_out_pipe.put(done)    

    def read_sm(self):
        """
        State machine to read data from memory
        """
        while True:
            # wait to receive a read request
            addr = yield self.r_in_pipe.get()
            # model read latency
            for i in range(self.read_latency):
                yield self.wait_clock()
            # try to read data from memory
            if addr in self.mem.keys():
                data = self.mem[addr]
            else:
                print >> sys.stderr, "ERROR: BRAM read_sm: specified address {} is out of range".format(addr)
                data = None
            self.rd_count += 1
            # write data back
            self.r_out_pipe.put(data)

class FIFO(HW_sim_object):
    def __init__(self, env, period, r_in_pipe, r_out_pipe, w_in_pipe, w_out_pipe=None, maxsize=128, write_latency=1, read_latency=1, init_items=[]):
        super(FIFO, self).__init__(env, period)
        self.r_in_pipe = r_in_pipe
        self.r_out_pipe = r_out_pipe
        self.w_in_pipe = w_in_pipe
        self.w_out_pipe = w_out_pipe
        self.write_latency = write_latency
        self.read_latency = read_latency
        self.maxsize = maxsize
        self.items = init_items

        # register processes for simulation
        self.run()

    def run(self):
        self.env.process(self.push_sm())
        self.env.process(self.pop_sm())

    def push_sm(self):
        """
        State machine to push incoming data into the FIFO
        """
        while True:
            # wait to receive incoming data
            data = yield self.w_in_pipe.get()
            # model write latency
            for i in range(self.write_latency):
                yield self.wait_clock()
            # try to write data into FIFO
            if len(self.items) < self.maxsize:
                self.items.append(data)
            else:
                print >> sys.stderr, "ERROR: FIFO push_sm: FIFO full, cannot push {}".format(data)
            # indicate write_completion
            if self.w_out_pipe is not None:
                done = 1
                self.w_out_pipe.put(done)

    def pop_sm(self):
        """
        State machine to pop data out of the FIFO upon request
        """
        while True:
            # wait to receive a read request
            req = yield self.r_in_pipe.get()
            # model read latency
            for i in range(self.read_latency):
                yield self.wait_clock()
            # try to read head element
            if len(self.items) > 0:
                data = self.items[0]
                self.items = self.items[1:]
            else:
                print >> sys.stderr, "ERROR: FIFO pop_sm: attempted to read from empty FIFO"
                data = None
            # write data back
            self.r_out_pipe.put(data)

    def __str__(self):
        return str(self.items)

    # TODO: get_len()? is_empty()?

    def get_len(self):
        return len(self.items)
    
    def peek_front(self):
        if len(self.items):
            return self.items[0]
        else:
            return 0
    


# Peixuan 10292020
class PIFO(HW_sim_object):
    def __init__(self, env, period, r_in_pipe, r_out_pipe, w_in_pipe, w_out_pipe=None, maxsize=128, write_latency=1, read_latency=1, shift_latency=1, init_items=[]):
        super(PIFO, self).__init__(env, period)
        self.r_in_pipe = r_in_pipe
        self.r_out_pipe = r_out_pipe
        self.w_in_pipe = w_in_pipe
        self.w_out_pipe = w_out_pipe
        self.write_latency = write_latency
        self.read_latency = read_latency
        self.shift_latency = shift_latency
        self.maxsize = maxsize
        self.items = init_items

        # register processes for simulation
        self.run()

    def run(self):
        self.env.process(self.push_sm())
        self.env.process(self.pop_sm())

    def push_sm(self):
        """
        State machine to push incoming data into the PIFO
        """
        popped_data = 0

        while True:
            popped_data_valid = 0
            # wait to receive incoming data
            data = yield self.w_in_pipe.get()
            # model write latency
            for i in range(self.write_latency):
                yield self.wait_clock()
            # first enque the item
            self.items.append(data)
            # then insert in the correct position and shift (sorting)
            for i in range(self.shift_latency):
                yield self.wait_clock()
            #self.items.sort()
            self.items = sorted(self.items, key=lambda pkt: pkt.get_finish_time())
            if len(self.items) > self.maxsize : # Peixuan Q: what if len = maxsize, should we keep the data?
                popped_data = self.items.pop(len(self.items)-1)
                popped_data_valid = 1
            # indicate write_completion
            if self.w_out_pipe is not None:
                #if popped_data:
                #    self.w_out_pipe.put(popped_data)
                #    print ('popped_data: {0}'.format(popped_data))
                #else:
                    done = 1
                    self.w_out_pipe.put((done, popped_data, popped_data_valid)) # tuple

    def pop_sm(self):
        """
        State machine to pop data out of the PIFO upon request
        """
        while True:
            # wait to receive a read request
            req = yield self.r_in_pipe.get()
            # model read latency
            for i in range(self.read_latency):
                yield self.wait_clock()
            # try to read head element
            if len(self.items) > 0:
                data = self.items[0]
                self.items = self.items[1:]
            else:
                print >> sys.stderr, "ERROR: PIFO pop_sm: attempted to read from empty PIFO"
                data = None
            # write data back
            self.r_out_pipe.put(data)

    def __str__(self):
        return str(self.items)
    
    def peek_front(self):
        if len(self.items):
            return self.items[0]
        else:
            return 0

# Peixuan 11122020
# This is the base level (level 0), no pifo
class Base_level(HW_sim_object):
	# Public
    def __init__(self, env, period, granularity, fifo_size, fifo_r_in_pipe_arr, fifo_r_out_pipe_arr, \
        fifo_w_in_pipe_arr, fifo_w_out_pipe_arr, fifo_write_latency=1, fifo_read_latency=1, \
        fifo_check_latency=1, fifo_num=10, initial_vc=0):
        super(Base_level, self).__init__(env, period)
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

class Packet_descriptior:
    # Tuser + headpointer as pkt
    def __init__(self, address, tuser):
        self.address = address
        self.tuser = tuser
    
    def get_finish_time(self): # rank
        return self.tuser.rank
    
    def set_finish_time(self, finish_time):
        self.tuser.rank = finish_time
    
    def get_address(self): # head ptr
        return self.address
    
    def get_uid(self):
        return self.tuser.pkt_id
    
    def get_tuser(self):
        return self.tuser


class AXI_S_master(HW_sim_object):
    def __init__(self, env, period, out_pipe, bus_width, pkt_list):
        super(AXI_S_master, self).__init__(env, period)
        self.out_pipe = out_pipe
        self.bus_width = bus_width # Bytes

        # register the processes for simulation 
        self.run(pkt_list)

    def run(self, pkt_list):
        self.env.process(self.write_pkts(pkt_list))

    def write_pkts(self, pkt_list):
        """Send pkt_list over AXI_stream interface
        Inputs:
          - pkt_list : list of tuples of the form (scapy pkt, Tuser object)
        """
        while True:
            # wait for the next transmission
            yield self.wait_clock()

            # send one word at a time
            if len(pkt_list) == 0:
                # no more data to send so send blanks
                tdata = '\x00'*self.bus_width
                tuser = Tuser(0, 0, 0)
                msg = AXI_S_message(tdata,0,0,0,tuser)
                self.out_pipe.put(msg)
            else:
                # send packets
                pkt = pkt_list[0]
                yield self.env.process(self.send_pkt(pkt))
                # remove the pkt we just sent from the pkt_list
                pkt_list = pkt_list[1:]

    def send_pkt(self, pkt_tuple):
        """Send a single packet (and associated metadata over AXI_stream interface)
        Input:
          - pkt_tuple: 0th element is a scapy packet, 1st element is a Tuser object
                       for that packet
        """
        pkt_str = str(pkt_tuple[0])
        tuser = pkt_tuple[1]
        while len(pkt_str) > self.bus_width:
            # at least one more word of this packet after this one
            tdata = pkt_str[0:self.bus_width]
            tvalid = 1
            tkeep = (1<<self.bus_width)-1
            tlast = 0
            msg = AXI_S_message(tdata, tvalid, tkeep, tlast, tuser)
            self.out_pipe.put(msg)
            yield self.wait_clock()
            pkt_str = pkt_str[self.bus_width:]
        # this is the last word of the packet
        tdata = pkt_str + '\x00'*(self.bus_width - len(pkt_str))
        tvalid = 1
        tkeep = (1<<len(pkt_str))-1
        tlast = 0
        msg = AXI_S_message(tdata, tvalid, tkeep, tlast, tuser)
        self.out_pipe.put(msg)

class AXI_S_slave(HW_sim_object):
    def __init__(self, env, period, in_pipe, bus_width):
        super(AXI_S_slave, self).__init__(env, period)
        self.in_pipe = in_pipe
        self.bus_width = bus_width # Bytes

        # register the processes for simulation
        self.run()

    def run(self):
        self.env.process(self.read_pkts())

    def read_pkts(self):
        while True:
            msg = yield self.in_pipe.get()
            print ('slave @ {:03d} msg received : {}'.format(self.env.now, msg))


class out_reg(HW_sim_object):
    def __init__(self, env, period, ins_in_pipe, ins_out_pipe, rem_in_pipe, rem_out_pipe, width=16, latency=1):
        super(out_reg, self).__init__(env, period)
        self.val = width*[None]
        self.ptrs = width*[None]
        self.ins_in_pipe = ins_in_pipe
        self.ins_out_pipe = ins_out_pipe
        self.rem_in_pipe = rem_in_pipe
        self.rem_out_pipe = rem_out_pipe
        self.width = width
        self.latency = latency
        self.num_entries = 0
        self.next = -1
        self.next_valid = 0
        self.busy = 0
        
        # register processes for simulation
        self.run()
    
    def run(self):
        self.env.process(self.insert())
        self.env.process(self.remove())

    def insert(self):
        while True:
            # Wait for insert request
            (val, ptrs) = yield self.ins_in_pipe.get()
            self.busy = 1
            self.next_valid = 0
            for i in range(self.latency):
                yield self.wait_clock()
            # Room available in register, just add the entry to the register
            if self.num_entries < self.width:
                self.val[self.num_entries] = val
                self.ptrs[self.num_entries] = ptrs
                self.num_entries += 1
                # -1 signals to the caller that there was room in the register to insert the entry without displacing another one
                self.ins_out_pipe.put((-1, [-1, -1]))
            else:
                # No room available
                # Find max value in register
                max_idx = self.val.index(max(self.val))
                max_val = self.val[max_idx]
                max_ptrs = self.ptrs[max_idx]
                # If new value is smaller than max
                if val < max_val:
                    # Replace max value with new value
                    self.val[max_idx] = val
                    self.ptrs[max_idx] = ptrs
                    # Return removed max value and data through pipe
                    # so can they can be inserted in skip list
                    self.ins_out_pipe.put((max_val, max_ptrs))
                else:
                    # Send new val and data through pipe so they can be inserted in skip list
                    self.ins_out_pipe.put((val, ptrs))
            # Output min value
            self.next = min(self.val[:self.num_entries])
            self.next_valid = 1
            self.busy = 0
            
    def remove(self):
        while True:
            # Wait for remove request
            yield self.rem_in_pipe.get()
            self.busy = 1
            self.next_valid = 0
#            for i in range(self.latency):
#                yield self.wait_clock()
            yield self.wait_clock()
            # Find min value in register
            min_idx = self.val.index(min(self.val[:self.num_entries]))
            min_val = self.val[min_idx]
            min_ptrs = self.ptrs[min_idx]
            # Shift up values below "hole" to pack the register
            self.val[min_idx:self.num_entries-1] = self.val[min_idx+1:self.num_entries]
            self.ptrs[min_idx:self.num_entries-1] = self.ptrs[min_idx+1:self.num_entries]
            self.val[self.num_entries-1] = None
            self.num_entries -= 1
            if self.num_entries > 0:
                self.next = min(self.val[:self.num_entries])
                self.next_valid = 1
            self.busy = 0
           
            # Send removed value through pipe
            self.rem_out_pipe.put((min_val, min_ptrs))

def pad_pkt(pkt, size):
    if len(pkt) >= size:
        return pkt
    else:
        return pkt / ('\x00'*(size - len(pkt)))

