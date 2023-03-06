from BittideFrame import BittideFrame
from collections import deque


class Buffer:
    def __init__(self, size, initialOcc, localNode, remoteNode):
        self.size = size
        self.dataq = deque(maxlen=size)
        self.initialOcc = initialOcc
        self.localNode = localNode
        self.remoteNode = remoteNode
        for i in range(initialOcc):
            self.dataq.appendleft(BittideFrame(sender_timestamp=-1, signals=[]))
    
    def receive(self, frame : BittideFrame):
        self.dataq.appendleft(frame)
    
    def send(self, timestamp, signals : list = []) -> tuple[BittideFrame,BittideFrame]: #data popped, data sent
        consumedFrame = self.dataq.pop()
        newSendFrame = BittideFrame(sender_timestamp = timestamp, signals = list)
        # if consumedFrame.sender_timestamp != -1:
        #     print("Received data sent from node " + self.remoteNode + " at " + str(consumedFrame.sender_timestamp) + " at local time " + str(timestamp))
        #     print("UGN " + self.localNode + "," +  self.remoteNode + " is " + str(timestamp - consumedFrame.sender_timestamp))
        return (consumedFrame,newSendFrame)

    def get_initial_occupancy(self):
        return self.initialOcc
    
    def get_occupancy(self):
        return len(self.dataq)

    def get_occupancy_as_percent(self):
        return 100 * self.get_occupancy() / self.size