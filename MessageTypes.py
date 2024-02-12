
class BackPressureMessage():
    def __init__(self, sourceNode, destNode, destTime, timestamp):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.destTime = destTime
        self.timestamp=timestamp

class WaitingMessage():
    def __init__(self, sourceNode, destNode, destTime, value):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.destTime = destTime
        self.value = value