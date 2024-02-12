from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque

class PIDController(Controller.Controller):
    def __init__(self, name, kp, ki, i_win, kd, d_step, offset):
        super().__init__(name)
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
        self.buffer_deadzone = 0

    def step(self,buffers) -> ControlResult:
        buffer_vals = []
        for buffer in buffers:
            # if buffers[buffer].live == False:
            #     return ControlResult(0, True)
            buffer_error = buffers[buffer].get_occupancy()- buffers[buffer].get_initial_occupancy()
            if (abs(buffer_error) <= self.buffer_deadzone): buffer_error = 0
            buffer_vals.append(buffer_error)
                
        if (len(buffer_vals) > 0):
            err = np.mean(buffer_vals)
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

        else: c = 0
        self.last_c = c
        
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c