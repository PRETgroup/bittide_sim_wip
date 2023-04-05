from Buffer import Buffer
from BittideFrame import BittideFrame

class Output:
    def __init__(self, nextStep, messages):
        self.nextStep = nextStep
        self.messages = messages

class Node:
    def __init__(self, name, buffers, initialFreq, server):
        self.name = name
        self.controller = None
        self.server = server
        self.freq = initialFreq
        self.phase = 0
        self.lastWasSkip = False
        self.buffers = []
        self.current_delays = {}
        for buffer in buffers:
            self.buffers.append(Buffer(buffer.size, buffer.initialOcc, name, buffer.remoteNode, server)) #FIXME: make this mapped to label rather than index
            self.current_delays[(name, buffer.remoteNode)] = 0
    
    def set_controller(self,controller):
        self.controller = controller

    def buffer_receive(self, index, value):            
        self.buffers[index].receive(value)
    
    def step(self):
        # print(self.name)
        if self.controller is None:
            print("Step attempted without an assigned controller! Exiting...")
            exit(0)
        controlResult = self.controller.step(self.buffers)
        self.freq += controlResult.freq_correction
        if controlResult.do_tick:
            self.phase += 1
            if (self.freq <= 1): self.freq = 1 #cap negative frequencies to prevent negative time deltas
            
            all_outputs_to_line = []
            all_inputs_to_fsm = []
            #first during a tick, we provide the local (networked) machine with some inputs from the head of our buffer
            for buffer in self.buffers:
                inboundBuff : BittideFrame = buffer.pop()
                if inboundBuff.sender_timestamp != -1:
                    self.current_delays[buffer.getId()] = self.phase - inboundBuff.sender_timestamp
                else: self.current_delays[buffer.getId()] = 0
                all_inputs_to_fsm.extend(inboundBuff.signals)

            #now we run the tick on the networked node:
            if (self. server is not None):
                outputs_from_fsm = self.server.run_node_tick(self.name, all_inputs_to_fsm)
            else:
                outputs_from_fsm = []

            for buffer in self.buffers:
                sent_frame = buffer.getSendMessage(self.phase, outputs_from_fsm)
                all_outputs_to_line.append(sent_frame)
            self.lastWasSkip = False
            return Output(1 / self.freq, all_outputs_to_line)
        else:
            self.lastWasSkip = True 
            return Output(1 / self.freq, None)
    
    def get_frequency(self):
        if self.lastWasSkip:
            return 0
        return self.freq
    
    def get_control_value(self):
        return self.controller.get_control()
    
    def get_logical_delays(self):
        delays = []
        for buffer in self.buffers:
            delays.append(self.current_delays[buffer.getId()])
        return delays
    
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
