from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque

class PIDController(Controller.Controller):
    def __init__(self, name, node, kp, ki, i_win, kd, d_step, offset):
        super().__init__(name, node, "PID")
        self.kp = kp
        self.ki = ki
        self.kd = kd
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
            if buffers[buffer].running == True:
                buffer_vals.append(buffers[buffer].get_occupancy_as_percent())
                
        if (len(buffer_vals) > 0):
            occ = np.mean(buffer_vals)
            if (self.prev_occ == -1): self.prev_occ = occ
            err = occ - self.prev_occ
            self.integral_window.append(err) #dt is always one
            self.integral = occ - 50

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
        
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c