from dataclasses import dataclass

@dataclass
class ControlResult:
    freq_correction: float
    do_tick : bool

class Controller:
    def __init__(self, name):
        self.name = name
    
    def step(self, buffers) -> ControlResult :
        return ControlResult