from BittideFrame import BittideFrame
from collections import deque


class Buffer:
    def __init__(self, size, initialOcc, localNode, remoteNode, server):
        self.size = size
        self.dataq = deque(maxlen=size)
        self.initialOcc = initialOcc
        self.server = server
        self.localNode = localNode
        self.remoteNode = remoteNode
        self.live = False
        for i in range(initialOcc):
            self.dataq.appendleft(BittideFrame(sender_timestamp=-1, signals=[]))

    def getId(self):
        return (self.localNode, self.remoteNode)
    
    def receive(self, frame : BittideFrame):
        self.live = True
        self.dataq.appendleft(frame)
    
    def pop(self) -> BittideFrame:
        if self.live:
            return self.dataq.pop()
        else: return BittideFrame(-1,[])
    
    def peek_newest_timestamp(self) -> int:
        return self.dataq[0].sender_timestamp
    
    def getSendMessage(self, timestamp, output_signals) -> BittideFrame: #data sent to the simulated medium
        newSendFrame = BittideFrame(sender_timestamp = timestamp, signals=output_signals)
        return newSendFrame

    def get_initial_occupancy(self):
        return self.initialOcc
    
    def get_occupancy(self):
        return len(self.dataq)

    def get_occupancy_as_percent(self):
        return 100 * self.get_occupancy() / self.size