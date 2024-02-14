from Controllers.Controller import Controller

class RuntimeInterchage:
    def __init__(self, name):
        self.name = name
    
    def checkPolicies(self, current_controller : Controller) -> Controller:
        return Controller