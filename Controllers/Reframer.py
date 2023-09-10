from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque


from enum import Enum
 
class Phase(Enum):
    STABLE = 0,
    UNSTABLE = 1,
    WAITING = 2,
    REFRAMING = 3,

class Reframer(Controller.Controller):
    def __init__(self, name, kp : float, settle_time : float, settle_distance : float, wait_time : float):
        super().__init__(name)
        self.kp = kp
        self.settle_time = settle_time
        self.settle_distance = settle_distance
        self.wait_t = 0
        self.wait_max = wait_time
        self.settle_count = 0
        self.correction_value = 0
        self.last_c = 0
        self.integral = 0
        self.prev_occ = -1
        self.phase = Phase.UNSTABLE

        self.sliding_window = deque(maxlen=5) 

    def step(self,buffers):
        buffer_vals = []
        for buffer in buffers:
            if buffers[buffer].live == True:
                buffer_vals.append(buffers[buffer].get_occupancy())
        if (len(buffer_vals) > 0):
            occ = np.mean(buffer_vals)
            if (self.prev_occ == -1) : self.prev_occ = occ #first cycle initialisation
            err = occ - self.prev_occ
            pterm = self.kp * err
            self.integral += err
            self.prev_occ = occ
            self.sliding_window.appendleft(err)
            drift = abs(sum(self.sliding_window) / len(self.sliding_window))
            if (self.phase == Phase.STABLE):
                if abs(self.integral) > 4:
                    print("instability!")
                    self.phase = Phase.UNSTABLE
            elif (self.phase == Phase.UNSTABLE):
                if drift <= self.settle_distance:
                    self.settle_count += 1
                else:
                    self.settle_count = 0

                if self.settle_count >= self.settle_time:
                    self.frozen_integral = self.integral
                    print("\nIntegral frozen at %f\n" % (occ - buffers.get(list(buffers.keys())[0]).initialOcc))
                    self.phase = Phase.WAITING

            elif (self.phase == Phase.WAITING):
                self.wait_t += 1
                if self.wait_t >= self.wait_max:
                    self.phase = Phase.REFRAMING
                    self.correction_value = self.kp * self.frozen_integral 
                    self.settle_count = 0
                    print("\nEntering reframing phase.")

            elif (self.phase == Phase.REFRAMING):
                if abs(err) <= self.settle_distance:
                    self.settle_count += 1
                else:
                    self.settle_count = 0

                if self.settle_count >= self.settle_time:
                    print("\n Returning to stable phase")
                    self.settle_count = 0
                    self.phase = Phase.STABLE

            c =  pterm + self.correction_value
            self.correction_value = 0

        else: c = 0
        self.last_c = c
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c