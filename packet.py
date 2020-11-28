class Packet_descriptior:
    # Tuser + headpointer as pkt
    def __init__(self, address, tuser):
        self.address = address
        self.tuser = tuser
    
    def get_finish_time(self, debug): # rank
        tuser = self.tuser
        if debug:
            print("tuser = {}".format(tuser))
        return tuser.rank
        #return self.tuser.rank
    
    def set_finish_time(self, finish_time):
        self.tuser.rank = finish_time
    
    def get_address(self): # head ptr
        return self.address
    
    def get_uid(self):
        return self.tuser.pkt_id
    
    def get_tuser(self):
        return self.tuser