import numpy as np
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

def get_hypothetical_occupancy_as_percent(buffers, num_blocked):
        occupancies = []
        for buffer in buffers:
            occupancies.append((buffers[buffer].get_occupancy() - num_blocked) /  buffers[buffer].size * 100)
        return np.mean(occupancies)

class FFP(Controller.Controller):
    def __init__(self, name, node):
        super().__init__(name, node, "FFP")
        self.num_tokens_blocked = 0

    def step(self,buffers) -> ControlResult:
         # check that all local buffers are not empty and remote are not full in the worst case
        if isEmpty(buffers):
            self.num_tokens_blocked += 1
            return ControlResult(0, False)
        if isFull(self.node.outgoing_links, self.node.backpressure_links,self.node.phase):
            self.num_tokens_blocked += 1
            return ControlResult(0, False)
        return ControlResult(0, True)
    
    
    def get_control(self):
        return 0