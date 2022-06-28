from Controllers import Controller
import numpy as np
from collections import deque

class PIDController(Controller.Controller):
    def __init__(self, name, kp, ki, i_win, kd, d_step, midpoint, offset):
        super().__init__(name)
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_window = deque([0] * i_win, maxlen=i_win)
        self.diff_window = deque([0] * d_step, maxlen=d_step)
        self.midpoint = midpoint
        self.offset = offset
        
    def step(self, occupancies):
        ri = np.mean([(occ - self.midpoint) for occ in occupancies]) #error term: average distance from midpoint
        
        self.integral_window.append(ri) #dt is always one
        
        pterm = self.kp * ri
        iterm = self.ki * sum(self.integral_window)
        dterm = self.kd * (ri - self.diff_window.popleft())
        self.diff_window.append(ri)
        
        c =  pterm + iterm + dterm + self.offset
        
        return int(c)