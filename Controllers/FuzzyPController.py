# File: Controllers/FuzzyPController.py

import numpy as np
from Controllers.Controller import Controller, ControlResult # Assuming this path is correct

class FuzzyPController(Controller):
    def __init__(self, name, node, setpoint=50.0, error_input_gain=0.2, control_output_gain=-1.5):
        """
        Initializes the Fuzzy P Controller for percentage-based occupancy.

        Args:
            name (str): Name of the controller.
            node (object): The node object this controller is associated with.
            setpoint (float): Target buffer occupancy as a percentage (e.g., 50.0 for 50%).
            error_input_gain (float): Scales raw percentage error to fuzzy logic's UoD.
                                      For raw error +/-50% to scaled +/-10, gain is 10/50 = 0.2.
            control_output_gain (float): Scales fuzzy logic's output to final control action.
                                         (e.g., 15-30 to match Kp of 0.15-0.3).
        """
        super().__init__(name, node, "FuzzyP")
        self.setpoint = float(setpoint)
        self.error_input_gain = float(error_input_gain)
        self.control_output_gain = float(control_output_gain)
        self.last_c = 0.0

    def _calculate_fuzzy_output(self, scaled_error):
        """
        Computes control output from scaled_error using fuzzy logic.
        Based on fuzzyPController.m with UoD -10 to 10 for scaled error.
        INPUT:  scaled_error - Error signal, scaled to roughly [-10, 10]
        OUTPUT: u_out        - Control action, typically in [-5, 5] before output gain
        """
        e = scaled_error

        # Membership functions based on MATLAB UoD -10 to 10
        mu_NL = 0.0
        if e <= -10: # mu_NL = mf(e, -10, -10, -5)
            mu_NL = 1.0
        elif -10 < e < -5:
            mu_NL = (-5 - e) / (-5 - (-10))

        mu_NS = 0.0
        if -10 < e < 0: # mu_NS = mf(e, -10, -5, 0)
            if e <= -5:
                mu_NS = (e - (-10)) / (-5 - (-10))
            else: 
                mu_NS = (0 - e) / (0 - (-5))

        mu_ZE = 0.0
        if -5 < e < 5: # mu_ZE = mf(e, -5, 0, 5)
            if e <= 0:
                mu_ZE = (e - (-5)) / (0 - (-5))
            else: 
                mu_ZE = (5 - e) / (5 - 0)

        mu_PS = 0.0
        if 0 < e < 10: # mu_PS = mf(e, 0, 5, 10)
            if e <= 5:
                mu_PS = (e - 0) / (5 - 0)
            else: 
                mu_PS = (10 - e) / (10 - 5)

        mu_PL = 0.0
        if e >= 10: # mu_PL = mf(e, 5, 10, 10)
            mu_PL = 1.0
        elif 5 < e < 10:
            mu_PL = (e - 5) / (10 - 5)

        # Control values (singletons)
        u_NL = -5
        u_NS = -2.5
        u_ZE = 0.0
        u_PS = 2.5     
        u_PL = 5

        numerator = (mu_NL * u_NL + mu_NS * u_NS + mu_ZE * u_ZE +
                     mu_PS * u_PS + mu_PL * u_PL) #
        denominator = mu_NL + mu_NS + mu_ZE + mu_PS + mu_PL #

        if denominator != 0:
            u_out = numerator / denominator #
        else:
            if e >= 10: 
                u_out = u_PL
            elif e <= -10: 
                u_out = u_NL
            else:
                u_out = 0.0 # Default if no rule fires
        return u_out

    def step(self, buffers_dict) -> ControlResult: # Renamed for clarity
        buffer_vals_percent = []
        # buffers_dict is expected to be the self.buffers dictionary from the Node object
        for buffer_key in buffers_dict: 
            buffer_obj = buffers_dict[buffer_key]
            if hasattr(buffer_obj, 'running') and buffer_obj.running:
                 # This MUST return percentage (0-100) for this controller config to be correct
                buffer_vals_percent.append(buffer_obj.get_occupancy_as_percent())

        control_action = 0.0
        if len(buffer_vals_percent) > 0:
            current_occupancy_percent = np.mean(buffer_vals_percent)

            # Calculate raw error in percentage terms
            # error > 0 means occupancy is below setpoint (needs positive action to increase freq/fill)
            # error < 0 means occupancy is above setpoint (needs negative action to decrease freq/slow fill)
            error_percent = self.setpoint - current_occupancy_percent

            # Scale error for fuzzy logic input (target: +/-50% raw error -> +/-10 scaled error)
            scaled_error_for_fuzzy = error_percent * self.error_input_gain

            # Get base fuzzy action (typically in -5 to 5 range)
            fuzzy_output_base = self._calculate_fuzzy_output(scaled_error_for_fuzzy)

            # Scale fuzzy output to final control action
            control_action = fuzzy_output_base * self.control_output_gain
            
            # # Optional: Print for debugging (ensure Node.py passes time 't' if used)
            # current_time = 0 # Placeholder if time 't' is not passed to this step method
            # print(f"T={current_time:.3f} Node {self.name}: Occ%={current_occupancy_percent:.1f}, SetPt%={self.setpoint:.1f}, RawErr%={error_percent:.1f}, ScaledErr={scaled_error_for_fuzzy:.2f}, FuzzyBase={fuzzy_output_base:.2f}, FreqCorr={control_action:.2f}")

        self.last_c = control_action
        return ControlResult(freq_correction=control_action, do_tick=True)

    def get_control(self):
        return self.last_c