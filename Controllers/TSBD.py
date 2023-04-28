from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque

class TSBD(Controller.Controller):
    def __init__(self, name, node):
        super().__init__(name)
        self.node = node
        for buffer in node.buffers:
            buffer.live = True #FFP buffers should never have an inactive state
    def step(self,buffers) -> ControlResult:
         # check that all local buffers are not empty and remote are not full in the worst case
        for buffer in buffers:
            if buffer.get_occupancy() == 0:
                return ControlResult(0, False)
            worst_case_occ = buffer.initialOcc - buffer.peek_newest_timestamp() + self.node.phase - self.node.current_delays[buffer.getId()]
            if (worst_case_occ > buffer.size):
                return ControlResult(0, False)
        return ControlResult(0, True)
    
    def get_control(self):
        return 0