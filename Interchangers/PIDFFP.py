from Interchangers.RuntimeInterchange import *
from Controllers import FFP
from Controllers import PIDControl

class PIDFFP(RuntimeInterchage):
    def __init__(self, name):   
        #specify the controllers which the config must load
        required_controllers = {
            "PID1" : ControllerInstance(None,False,1),
            "FFP1" : ControllerInstance(None,False,2)
        }
        super().__init__(name, required_controllers)
        
    def check_policies(self, node) -> list:
        possible_choices = ["PID1"]
        
        #overflow/underflow detection
        if FFP.isEmpty(node.buffers) \
            or FFP.isFull(node.outgoing_links, 
                          node.backpressure_links, node.phase):
            possible_choices.append("FFP1")
        return possible_choices