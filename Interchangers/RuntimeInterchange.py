from attr import dataclass
from Controllers.Controller import Controller

@dataclass
class ControllerInstance:
    instance: Controller
    suspended : bool
    priority : int

class InterchangePolicy():
    def check_violations(node) : bool
    
class RuntimeInterchage:
    def __init__(self, name, controllers : dict):
        self.name = name
        #specify the controllers which the config must load
        self.controllers = controllers
        self.previous_controller = None

        self.all_controllers_loaded = False
        self.num_loaded_controllers = 0
        self.num_controllers_max = len(self.controllers)
    
    #initial setup, config loader populates the controller instances
    def register_controller(self, controller_name : str, controller : Controller):
        print("Registered controller " + controller_name)
        if controller_name.upper() in self.controllers:
            self.num_loaded_controllers += 1
            if self.num_loaded_controllers >= self.num_controllers_max:
                self.all_controllers_loaded = True

            self.controllers[controller_name.upper()].instance = controller
    
    # behaviour overridden by child class
    def check_policies(current_controllers, buffers):
        return None
    
    # each policy encoded using simple if statements, should be changed to some kind of RI format later
    def choose_controller(self, node) -> Controller:
        if self.all_controllers_loaded == False:
            print("Missing some enforcer controllers. Exiting")
            exit(0)

        controller_choices = self.check_policies(node)

        #from the controllers not suspended, pick a control strategy by priority or randomly
        highest_priority = -1
        current_selection = None
        for choice in controller_choices:
            if self.controllers[choice].priority > highest_priority:
                current_selection = choice
                highest_priority = self.controllers[choice].priority
        self.previous_controller = current_selection
        return current_selection
    
    def on_controller_selected(self, selected_controller, node): #no default behaviour, for interchange
        return
    
    def step(self, node) -> float:
        next_controller = self.choose_controller(node)
        self.on_controller_selected(next_controller, node)
        chosen_output = None
        
        # do a step on all non-suspended controllers, returning only the chosen controller
        for controller in self.controllers:
            if self.controllers[controller].suspended == False:
                control_value = self.controllers[controller].instance.step(node.buffers)

            if controller is next_controller:
                chosen_output = control_value

        if chosen_output is None:
            print("Error: No valid policy for control")
            exit(0)
        return chosen_output