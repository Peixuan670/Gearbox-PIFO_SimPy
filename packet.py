class Packet_discreptor:
    def __init__(self, address, tuser):
        self.address = address
        self.tuser = tuser
    
    def getFinishTime(self): # rank
        return self.tuser.rank
    
    def setFinishTime(self, finish_time):
        self.tuser.rank = finish_time
    
    def getAddress(self): # head ptr
        return self.address
    
    def getUid(self):
        return self.tuser.pkt_id
    
    def getTuser(self):
        return self.tuser

'''
    class pkt:
    	finish_time
    	address
    	uid?
    '''

        