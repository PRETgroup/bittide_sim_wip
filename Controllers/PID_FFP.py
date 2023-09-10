from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque


class PIDFFPController(Controller.Controller):
    def __init__(self, name,node, kp, ki, i_win, kd, d_step, offset):
        super().__init__(name)
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.node = node
        self.mode = 0
        self.integral_window = deque([0] * i_win, maxlen=i_win)
        self.integral = 0
        self.d_step = d_step
        self.diff_window = deque([0] * d_step, maxlen=d_step)
        self.offset = offset
        self.last_c = 0
        self.prev_occ = -1
    def step(self,buffers) -> ControlResult:
        buffer_vals = []
        for buffer in buffers:
            if buffers[buffer].get_occupancy() == 0:
                #self.mode = 1
                return ControlResult(0, False)
            if buffers[buffer].live == True:
                buffer_vals.append(buffers[buffer].get_occupancy())
        if (len(buffer_vals) > 0) and (self.mode == 0):
            occ = np.mean(buffer_vals)
            if (self.prev_occ == -1) : self.prev_occ = occ #first cycle initialisation
            err = occ - self.prev_occ
            self.integral_window.append(err) #dt is always one
            self.integral += err

            pterm = self.kp * err
            if (len(self.integral_window) > 0):
                iterm = self.ki * sum(self.integral_window)
            else:
                iterm = self.ki * self.integral
            dterm = self.kd * (err - self.diff_window.popleft())/self.d_step
            self.diff_window.append(err)
            c =  pterm + iterm + dterm + self.offset
            self.prev_occ = occ
        else: c = 0
        self.last_c = c
        
        for outgoing_link in self.node.outgoing_links:
            target_link = self.node.outgoing_links[outgoing_link]
            worst_case_occ = target_link.destInitialOcc - self.node.backpressure_links[target_link.destNode] + self.node.phase
            if (worst_case_occ >= target_link.destCapacity):
                #self.mode = 1
                return ControlResult(0, False)
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c