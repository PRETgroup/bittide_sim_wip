from dataclasses import dataclass

@dataclass
class ControlResult:
    freq_correction: float
    do_tick : bool

class Controller:
    def __init__(self, name, node, type):
        self.name = name
        self.node = node
        self.type = type
    
    def step(self, buffers) -> ControlResult :
        return ControlResult