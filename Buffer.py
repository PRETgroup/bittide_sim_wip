class BufferSettings:
    def __init__(self, size, initialOcc):
        self.size = size
        self.initialOcc = initialOcc

class Buffer:
    def __init__(self, size, initialOcc):
        self.size = size
        self.occ = initialOcc
    
    def receive(self, value):
        self.occ += 1
        
        # print("Rcv msg", self.occ)

        if self.occ > self.size:
            print("OVERFLOW DETECTED")
    
    def send(self):
        self.occ -= 1
        
        # print("Send msg", self.occ)

        if self.occ < 0:
            print("UNDERFLOW DETECTED")

        return "1"

    def get_occupancy(self):
        return self.occ

    def get_occupancy_as_percent(self):
        return 100 * self.occ / self.size