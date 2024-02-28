from collections import deque
from enum import Enum
from attr import dataclass
import numpy as np
from Controllers.Reframer import ReframerPhase
from Interchangers.RuntimeInterchange import *
from Controllers import FFP

class OverflowPolicy(InterchangePolicy):
    class States(Enum):
        Singleton = 0
    def __init__(self):
        self.state = self.States.Singleton

    def check_violations(self, node):
        if FFP.isEmpty(node.buffers) \
            or FFP.isFull(node.outgoing_links, 
                          node.backpressure_links, node.phase):
            return True
        else: return False

class SteadyStateErrorPolicy(InterchangePolicy):
    class States(Enum):
        IDLE = 0
        TIMER_EXPIRED = 1
    def __init__(self):
        self.state = self.States.IDLE
        self.counter = 0
        self.prev_occ = None
        self.sliding_window = deque(maxlen=5) 
    def check_violations(self, node, reframer):
        violation = False
        if self.state == self.States.TIMER_EXPIRED: return violation
        occ = node.get_average_occupancy_as_percent()
        if self.prev_occ is not None and (abs(occ-50) > 1):
            #if our buffer occupancy is not changing, it's a good time to do a reframing
            if self.state == self.States.IDLE:
                err = abs(self.prev_occ - occ)
                self.sliding_window.appendleft(err)
                drift = abs(sum(self.sliding_window) / len(self.sliding_window))
                if drift <= reframer.settle_distance:
                    self.counter += 1
                    if self.counter >= reframer.settle_time:
                        violation = True
                        reframer.settle_count = self.counter
                        self.state = self.States.TIMER_EXPIRED
                else: self.counter = 0
            else: violation = True
        self.prev_occ = occ
        return violation
    

class REFRAMING_INTERCHANGER(RuntimeInterchage):
    def __init__(self, name):        
        #specify the controllers which the config must load
        required_controllers = {
            "PID1" : ControllerInstance(None,False,1),
            "FFP1" : ControllerInstance(None,False,2),
            "REFRAMER1" : ControllerInstance(None,True,3)
        }
        self.overflow_policy = OverflowPolicy()
        self.ss_error_policy = SteadyStateErrorPolicy()
        super().__init__(name, required_controllers)
        
    def check_policies(self, node) -> list:
        possible_choices = []
        
        #we should not transition from FFP back into PID immediately, or it will oscillate about the extremity
        if self.previous_controller != "FFP1":
            possible_choices.append("PID1")
        else:
            possible_choices.append("FFP1")


        #reset suspensions (default on/off)
        self.controllers["PID1"].suspended = False
        self.controllers["FFP1"].suspended = True
        self.controllers["REFRAMER1"].suspended = True

        #overflow/underflow detection
        if (self.overflow_policy.check_violations(node)):
            possible_choices.append("FFP1")

        #steady state error correction
        if (self.ss_error_policy.check_violations(node, self.controllers["REFRAMER1"].instance)):
            possible_choices.append("REFRAMER1")

        return possible_choices
    
    def on_controller_selected(self, selected_controller, node):
        self.controllers[selected_controller].suspended = False

        if selected_controller == "REFRAMER1":
            #self.controllers["REFRAMER1"].instance.integral = FFP.get_hypothetical_occupancy_as_percent(node.buffers,self.controllers["FFP1"].instance.num_tokens_blocked) - 50
            self.controllers["REFRAMER1"].suspended = False
            self.controllers["PID1"].suspended = True
        elif selected_controller == "FFP1":
            self.controllers["REFRAMER1"].suspended = True
            self.controllers["PID1"].suspended = True
         
