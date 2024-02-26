from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque


from enum import Enum

class IntReframerPhase(Enum):
    WAITING = 1,
    REFRAMING = 2,

#a cut-down reset to be controlled by the interchanger
class TriggeredReframer(Controller.Controller):
    def __init__(self, name, node, kp : float, settle_time : float, settle_distance : float, wait_time : float):
        super().__init__(name, node,"INTERCHANGEREFRAMER")
        self.kp = kp
        self.settle_time = settle_time
        self.settle_distance = settle_distance
        self.wait_t = 0
        self.wait_max = wait_time
        self.integral = 0
        self.correction_value = 0
        self.last_c = 0
        self.prev_occ = None
        self.phase = IntReframerPhase.WAITING

    def step(self,buffers):
        buffer_vals = []
        for buffer in buffers:
            buffer_vals.append(buffers[buffer].get_occupancy_as_percent())

        if (len(buffer_vals) > 0):
            occ = np.mean(buffer_vals)
            if (self.prev_occ == None) : self.prev_occ = occ #first cycle initialisation
            err = occ - self.prev_occ
            pterm = self.kp * err
            self.prev_occ = occ

            if (self.phase == IntReframerPhase.WAITING):
                self.wait_t += 1
                if self.wait_t >= self.wait_max:
                    self.phase = IntReframerPhase.REFRAMING
                    self.correction_value = self.kp * self.integral 
                    self.settle_count = 0
                    print("\nEntering reframing phase.")

            elif (self.phase == IntReframerPhase.REFRAMING):
                pass #do nothing until reset by interchanger

            c =  pterm + self.correction_value
            self.correction_value = 0

        else: c = 0
        self.last_c = c
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c