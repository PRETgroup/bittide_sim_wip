from Controllers import Controller
from Controllers.Controller import ControlResult
from collections import deque

def isFull(outgoing_links, backpressure_links, phase):
    for outgoing_link in outgoing_links:
        target_link = outgoing_links[outgoing_link]

        #only use the phase beginning when all bugfers are live?
        worst_case_occ = target_link.destInitialOcc - backpressure_links[target_link.destNode] + phase
        if (worst_case_occ >= target_link.destCapacity):
            return True
    return False

def isEmpty(buffers):
    for buffer in buffers:
        if buffers[buffer].get_occupancy() == 0:
            return True
    return False

class FFP(Controller.Controller):
    def __init__(self, name, node):
        super().__init__(name, node, "FFP")

    def step(self,buffers) -> ControlResult:
         # check that all local buffers are not empty and remote are not full in the worst case
        if isEmpty(buffers):
            return ControlResult(0, False)
        if isFull(self.node.outgoing_links, self.node.backpressure_links,self.node.phase):
            return ControlResult(0, False)
        return ControlResult(0, True)
    
    def get_control(self):
        return 0