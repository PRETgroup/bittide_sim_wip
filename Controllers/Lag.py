from Controllers import Controller
from Controllers.Controller import ControlResult
import numpy as np
from collections import deque

class LagController(Controller.Controller):
    def __init__(self, name, node, kp, ki, kd, lag_kp, lag_td, lead_kp, lead_td):
        super().__init__(name, node, "LAG")
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.d_step = 1
        self.diff_window = deque([0] * self.d_step, maxlen=self.d_step)
        self.last_c = 0
        self.prev_occ = -1
        self.lag_kp = lag_kp
        self.lag_td = lag_td
        self.lag_state = 0
        self.lead_kp = lead_kp
        self.lead_td = lead_td
        self.lead_state = 0

    def step(self,buffers) -> ControlResult:
        buffer_vals = []
        for buffer in buffers:
            if buffers[buffer].running == True:
                buffer_vals.append(buffers[buffer].get_occupancy_as_percent())
                
        if (len(buffer_vals) > 0):
            occ = np.mean(buffer_vals)
            if (self.prev_occ == -1): self.prev_occ = occ
            err = occ - self.prev_occ
            self.integral += err

            pterm = self.kp * err
            iterm = self.ki * self.integral
            dterm = self.kd * (err - self.diff_window.popleft())/self.d_step
            self.diff_window.append(err)

            # Lag Compensator
            self.lag_state += err * self.lag_td
            self.lead_state += err * self.lead_td
            lead_term = self.lead_kp * self.lead_state
            lag_term = self.lag_kp * self.lag_state * np.exp(-1 / self.lag_td)
            c =  pterm + iterm + dterm + lag_term + lead_term
            self.prev_occ = occ
        else: c = 0
        self.last_c = c
        
        return ControlResult(c, True)
    
    def get_control(self):
        return self.last_c