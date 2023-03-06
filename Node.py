from Buffer import Buffer
from BittideFrame import BittideFrame

class Output:
    def __init__(self, nextStep, messages):
        self.nextStep = nextStep
        self.messages = messages

class Node:
    def __init__(self, name, controller, buffers, initialFreq):
        self.name = name
        self.controller = controller

        self.freq = initialFreq
        self.phase = 0

        self.buffers = []
        for buffer in buffers:
            self.buffers.append(Buffer(buffer.size, buffer.initialOcc, name, buffer.remoteNode)) #FIXME: make this mapped to label rather than index
    
    def buffer_receive(self, index, value):
        self.buffers[index].receive(value)
    
    def step(self):
        # print(self.name)
        self.phase += 1
        occupancies = []
        initial_occs = []
        for buffer in self.buffers:
            occupancies.append(buffer.get_occupancy())
            initial_occs.append(buffer.get_initial_occupancy())
        

        self.freq += self.controller.step((occupancies,initial_occs))
        if (self.freq <= 1): self.freq = 1 #cap negative frequencies to prevent negative time deltas
        
        out = []
        inbound_frames = {}
        for buffer in self.buffers:
            received_frame, sent_frame = buffer.send(self.phase, [])
            out.append(sent_frame)
            inbound_frames[buffer.remoteNode] = received_frame
        

        return Output(1 / self.freq, out)
    
    def get_frequency(self):
        return self.freq
    
    def get_control_value(self):
        return self.controller.get_control()
    
    def get_occupancies(self):
        occupancies = []
        for buffer in self.buffers:
            occupancies.append(buffer.get_occupancy())
        
        return occupancies
    
    def get_occupancies_as_percent(self):
        occupancies = []
        for buffer in self.buffers:
            occupancies.append(buffer.get_occupancy_as_percent())
        
        return occupancies
