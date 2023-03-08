from Buffer import Buffer
from BittideFrame import BittideFrame

class Output:
    def __init__(self, nextStep, messages):
        self.nextStep = nextStep
        self.messages = messages

class Node:
    def __init__(self, name, controller, buffers, initialFreq, server):
        self.name = name
        self.controller = controller
        self.server = server
        self.freq = initialFreq
        self.phase = 0

        self.buffers = []
        for buffer in buffers:
            self.buffers.append(Buffer(buffer.size, buffer.initialOcc, name, buffer.remoteNode, server)) #FIXME: make this mapped to label rather than index
    
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
        
        all_outputs_to_line = []
        all_inputs_to_fsm = []
        #first during a tick, we provide the local (networked) machine with some inputs from the head of our buffer
        for buffer in self.buffers:
            inboundBuff : BittideFrame = buffer.pop()
            all_inputs_to_fsm.extend(inboundBuff.signals)

        #now we run the tick on the networked node:
        if (self. server is not None):
            outputs_from_fsm = self.server.run_node_tick(self.name, all_inputs_to_fsm)
        else:
            outputs_from_fsm = []

        for buffer in self.buffers:
            sent_frame = buffer.getSendMessage(self.phase, outputs_from_fsm)
            all_outputs_to_line.append(sent_frame)
               
        return Output(1 / self.freq, all_outputs_to_line)
    
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
