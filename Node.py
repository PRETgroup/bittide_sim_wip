from Buffer import Buffer
from BittideFrame import BittideFrame

class Output:
    def __init__(self, nextStep, phase, messages):
        self.nextStep = nextStep
        self.phase=phase
        self.messages = messages

def getSendMessage(timestamp, output_signals, sender_phys_time) -> BittideFrame: #data sent to the simulated medium
    newSendFrame = BittideFrame(sender_timestamp = timestamp, sender_phys_time=sender_phys_time, signals=output_signals)
    return newSendFrame

class Node:
    def __init__(self, name, buffers, initialFreq, server, outgoing_links):
        self.name = name
        self.controller = None
        self.runtime_enforcer = None

        self.server = server
        self.initialFreq = initialFreq
        self.freq = initialFreq
        self.phase = 0
        self.last_step_time = 0
        self.last_jitter = 0
        self.last_period = 0
        self.lastWasSkip = False
        self.buffers = {}
        self.current_delays = {}
        self.outgoing_links = outgoing_links
        self.backpressure_links = {}

        for outgoing_link in self.outgoing_links:
            target_link = self.outgoing_links[outgoing_link]
            self.backpressure_links[target_link.destNode] = 0
        for buffer in buffers:
            self.buffers[buffer.remoteNode] = (Buffer(buffer.size, buffer.initialOcc, name, buffer.remoteNode, server)) #FIXME: make this mapped to label rather than index
            self.current_delays[(name, buffer.remoteNode)] = 0
    
    def set_controller(self,controller):
        self.controller = controller
    
    def set_runtime_enforcer(self, runtime_enforcer):
        self.runtime_enforcer = runtime_enforcer

    def buffer_receive(self, index, value):
        try:         
            self.buffers[index].receive(value)
        except:
            print("No inbound buffer with index " + str(index) + " at node " + self.name)

    def backpressure_update(self, source_node, timestamp):
            #print("Updating backpressure value of " + str(timestamp) + " from node " + source_node + " to " + self.name)
            self.backpressure_links[source_node] = timestamp
        
    def step(self, steptime):
        # print(self.name)
        if self.controller is None:
            print("Step attempted without an assigned controller! Exiting...")
            exit(0)

        if self.runtime_enforcer is not None:
            self.controller = self.runtime_enforcer.checkPolicies(self.controller)   
        controlResult = self.controller.step(self.buffers)
        self.freq += controlResult.freq_correction

        if controlResult.do_tick:
            #telemetry###
            recent_period = steptime - self.last_step_time
            self.last_jitter = abs(recent_period - self.last_period)
            self.last_period = recent_period
            self.last_step_time = steptime
            #############

            self.phase += 1
            if (self.freq < 0.01): self.freq = 0.01 #cap negative frequencies to prevent negative time deltas
            
            all_inputs_to_fsm = []
            #first during a tick, we provide the local (networked) machine with some inputs from the head of our buffer
            for buffer in self.buffers:
                inboundBuff : BittideFrame = self.buffers[buffer].pop()
                if inboundBuff.sender_timestamp != -1:
                    self.current_delays[self.buffers[buffer].getId()] = self.phase - inboundBuff.sender_timestamp
                else: self.current_delays[self.buffers[buffer].getId()] = 0
                all_inputs_to_fsm.extend(inboundBuff.signals)
                self.buffers[buffer].add_latency_measurement(steptime-inboundBuff.sender_phys_time)

            #now we run the tick on the networked node:
            if (self. server is not None):
                outputs_from_fsm = self.server.run_node_tick(self.name, all_inputs_to_fsm)
            else:
                outputs_from_fsm = []


            sent_frame = getSendMessage(self.phase, outputs_from_fsm, steptime)
            self.lastWasSkip = False
            return Output(1 / self.freq, self.phase, sent_frame)
        else:
            self.lastWasSkip = True 
            return Output(1 / self.freq, self.phase, None)
    
    def get_frequency(self):
        if self.lastWasSkip:
            return 0
        return self.freq
    
    def get_control_value(self):
        return self.controller.get_control()
    
    def get_logical_delays(self):
        delays = []
        for buffer in self.buffers:
            delays.append(self.current_delays[self.buffers[buffer].getId()])
        return delays
    
    def get_occupancies(self):
        occupancies = []
        for buffer in self.buffers:
            occupancies.append(self.buffers[buffer].get_occupancy())
        
        return occupancies
    
    def get_latencies(self):
        latencies = []
        for buffer in self.buffers:
            latencies.append(self.buffers[buffer].last_latency)
        return latencies
    
    def get_occupancies_as_percent(self):
        occupancies = []
        for buffer in self.buffers:
            occupancies.append(self.buffers[buffer].get_occupancy_as_percent())
        
        return occupancies
