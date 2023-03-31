from numbers import Integral
from Controllers import Controller
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
        self.deadzone = 2
        self.last_c = 0
        self.prev_occ = -1
    def step(self, buffers_statuses, live : bool):
        occupancies, initial_occs = buffers_statuses
        occ = np.mean(occupancies)
        if live:
            if (self.prev_occ == -1) : self.prev_occ = occ #first cycle initialisation
            ri = occ - self.prev_occ
            self.integral_window.append(ri) #dt is always one
            self.integral += ri

            pterm = self.kp * ri
            if (len(self.integral_window) > 0):
                iterm = self.ki * sum(self.integral_window)
            else:
                iterm = self.ki * self.integral
            dterm = self.kd * (ri - self.diff_window.popleft())/self.d_step
            self.diff_window.append(ri)
            c =  pterm + iterm + dterm + self.offset
        else: c = 0
        self.last_c = c
        self.prev_occ = occ
        return c
    
    def get_control(self):
        return self.last_c