from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque

class TSBD(Controller.Controller):
    def __init__(self, name, node):
        super().__init__(name)
        self.node = node
        for buffer in node.buffers:
            node.buffers[buffer].live = True #FFP buffers should never have an inactive state\

    def step(self,buffers) -> ControlResult:
         # check that all local buffers are not empty and remote are not full in the worst case
        for buffer in buffers:
            if buffers[buffer].get_occupancy() == 0:
                return ControlResult(0, False)
        for outgoing_link in self.node.outgoing_links:
            target_link = self.node.outgoing_links[outgoing_link]
            worst_case_occ = target_link.destInitialOcc - self.node.backpressure_links[target_link.destNode] + self.node.phase
            # if self.name == "D":
            #         print("Predicted occ of E:")
            #         print(target_link.destInitialOcc)
            #         print(-self.node.backpressure_links[target_link.destNode])
            #         print( self.node.phase )
            #         print(-self.node.current_delays[buffers[buffer].getId()])
            #         print(worst_case_occ)
            if (worst_case_occ >= target_link.destCapacity):
                # if self.name == "n4":
                #     print("remote buffer " + self.node.name + "->" + target_link.destNode + " full!")
                #     print(target_link.destInitialOcc)
                #     print(-self.node.backpressure_links[target_link.destNode])
                #     print( self.node.phase )
                #     print(-self.node.current_delays[buffer.getId()])
                #     print(worst_case_occ)
                return ControlResult(0, False)
        return ControlResult(0, True)
    
    def get_control(self):
        return 0