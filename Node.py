from Buffer import Buffer

class Output:
    def __init__(self, nextStep, messages):
        self.nextStep = nextStep
        self.messages = messages

class Node:
    def __init__(self, name, controller, buffers, initialFreq):
        self.name = name
        self.controller = controller

        self.freq = initialFreq

        self.buffers = []
        for buffer in buffers:
            self.buffers.append(Buffer(buffer.size, buffer.initialOcc)) #FIXME: make this mapped to label rather than index
    
    def buffer_receive(self, index, value):
        self.buffers[index].receive(value)
    
    def step(self):
        # print(self.name)

        occupancies = []
        initial_occs = []
        for buffer in self.buffers:
            occupancies.append(buffer.get_occupancy())
            initial_occs.append(buffer.get_initial_occupancy())

        self.freq += self.controller.step((occupancies,initial_occs))
        if (self.freq <= 1): self.freq = 1 #cap negative frequencies to prevent negative time deltas
        
        out = []
        for buffer in self.buffers:
            val = buffer.send()
            out.append(val)
        

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
