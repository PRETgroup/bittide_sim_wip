from threading import local


class BufferSettings:
    def __init__(self, size, initialOcc):
        self.size = size
        self.initialOcc = initialOcc
        

class Buffer:
    def __init__(self, size, initialOcc):
        self.size = size
        self.initialOcc = initialOcc
        self.occ = initialOcc
        self.recent_send_time = -1
        self.total_sent = 0
        self.total_received = 0
        self.ugn = 0
    
    def receive(self, send_time):
        self.occ += 1
        self.recent_send_time = send_time
        self.total_received += 1
        # if self.occ > self.size:
        #     print("OVERFLOW DETECTED")
    
    def send(self, send_time):
        self.occ -= 1
        self.total_sent = self.total_sent + 1

        return send_time

    def get_initial_occupancy(self):
        return self.initialOcc
    
    def calculate_ugn(self, current_time):
        if (self.recent_send_time == -1):
            return 0
        time_diff = current_time - self.recent_send_time # = lambda + num_received - num_sent
        # print("\n Current: " + str(current_time) + ", sent:" + str(self.recent_send_time) + "\n")
        #self.ugn = self.initialOcc - (current_time - (self.recent_send_time - self.occ))
        self.ugn = time_diff
        #print("\ninitial: " + str(self.initialOcc) + ", current_time: " + str(current_time) + ", recent_send_time: " + str(self.recent_send_time) + ", occ: " + str(self.occ) + "\n")
        
    def get_ugn(self):
        return self.ugn
    
    def get_occupancy(self,current_time):
        # print("\n There are " + str(self.occ) + "in buffer and " + str(self.get_ugn(current_time)) + " on the line \n")
        return self.occ# + self.get_ugn(current_time)
    
    def get_occupancy_as_percent(self,current_time):
        return 100 * self.get_occupancy(current_time) / self.size