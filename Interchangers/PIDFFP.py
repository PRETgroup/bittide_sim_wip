from enum import Enum
from Interchangers.RuntimeInterchange import *
from Controllers import FFP
from Controllers import PIDControl

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

class PIDFFP(RuntimeInterchage):
    def __init__(self, name):   
        #specify the controllers which the config must load
        required_controllers = {
            "PID1" : ControllerInstance(None,False,1),
            "FFP1" : ControllerInstance(None,False,2)
        }
        super().__init__(name, required_controllers)
        self.overflow_policy = OverflowPolicy()
    
    def check_policies(self, node) -> list:
        possible_choices = ["PID1"]
        
        #reset suspensions (default on/off)
        self.controllers["PID1"].suspended = False
        self.controllers["FFP1"].suspended = False
        
        #overflow/underflow detection
        if (self.overflow_policy.check_violations(node)):
            possible_choices.append("FFP1")
            self.controllers["PID1"].suspended = True

        return possible_choices