class Controller:
    def __init__(self, name):
        self.name = name
    
    def step(self, occupancies, live : bool):
        return 0