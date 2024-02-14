from Interchange import *
from Controllers import FFP

class FFPPID(RuntimeInterchage):
    def checkPolicies(self, current_controller : Controller) -> Controller:
        next_controller = current_controller

        if current_controller.name == "PID":
            if FFP.isEmpty(current_controller.node.buffers) \
                or FFP.isFull(current_controller.node.outgoing_links, current_controller.node.backpressure_links, current_controller.node.phase):
                next_controller = FFP.FFP(current_controller.name, current_controller.node)
        elif current_controller.name == "FFP":
            pass

        return next_controller