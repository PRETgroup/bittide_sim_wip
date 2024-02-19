from Interchangers.RuntimeInterchange import *
from Controllers import FFP
from Controllers import PIDControl

class PIDFFP(RuntimeInterchage):
    def __init__(self, name):
        self.name = name
        self.all_controllers_loaded = False
        self.num_loaded_controllers = 0
        super().__init__(name)
        
        #specify the controller bank
        self.required_controllers = {
            "PID1" : PIDControl.PIDController | None,
            "FFP1" : FFP.FFP | None
        }
        self.num_controllers_max = len(self.required_controllers)

    def register_controller(self, controller_name : str, controller : Controller):
        print("Registered controller " + controller_name)
        if controller_name.upper() in self.required_controllers:
            self.num_loaded_controllers += 1
            if self.num_loaded_controllers >= self.num_controllers_max:
                self.all_controllers_loaded = True
            self.required_controllers[controller_name.upper()] = controller


    def checkPolicies(self, current_controller : Controller) -> Controller:
        if self.all_controllers_loaded == False:
            print("Missing some enforcer controllers. Exiting")
            exit(0)
        next_controller = current_controller
        if current_controller.type == "PID":
            if FFP.isEmpty(current_controller.node.buffers) \
                or FFP.isFull(current_controller.node.outgoing_links, current_controller.node.backpressure_links, current_controller.node.phase):
                print("Overflow/Underflow detected: Switching to FFP")
                next_controller = self.required_controllers["FFP1"]
        elif current_controller.type == "FFP":
            if (not FFP.isEmpty(current_controller.node.buffers)) and (not FFP.isFull(current_controller.node.outgoing_links, current_controller.node.backpressure_links, current_controller.node.phase)):
                next_controller = self.required_controllers["PID1"]

        return next_controller