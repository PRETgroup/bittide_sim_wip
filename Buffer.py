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
        for i in range(initialOcc):
            self.dataq.appendleft(BittideFrame(sender_timestamp=-1, signals=[]))

    def getId(self):
        return (self.localNode, self.remoteNode)
    
    def receive(self, frame : BittideFrame):
        self.dataq.appendleft(frame)
    
    def pop(self) -> BittideFrame:
        return self.dataq.pop()
    
    def getSendMessage(self, timestamp, output_signals) -> BittideFrame: #data sent to the simulated medium
        newSendFrame = BittideFrame(sender_timestamp = timestamp, signals=output_signals)
        # if consumedFrame.sender_timestamp != -1:
        #     print("Received data sent from node " + self.remoteNode + " at " + str(consumedFrame.sender_timestamp) + " at local time " + str(timestamp))
        #     print("UGN " + self.localNode + "," +  self.remoteNode + " is " + str(timestamp - consumedFrame.sender_timestamp))
        return newSendFrame

    def get_initial_occupancy(self):
        return self.initialOcc
    
    def get_occupancy(self):
        return len(self.dataq)

    def get_occupancy_as_percent(self):
        return 100 * self.get_occupancy() / self.size