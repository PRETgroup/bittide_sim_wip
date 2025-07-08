import numpy as np
from Controllers.Controller import Controller, ControlResult

class FuzzyPIController(Controller):
    def __init__(self, name, node, setpoint=50.0,
                 error_input_gain=0.2, derror_input_gain=2.5,
                 dcontrol_output_gain=-0.5):
        super().__init__(name, node, "FuzzyPI")
        self.setpoint = float(setpoint)
        self.error_input_gain = float(error_input_gain)
        self.derror_input_gain = float(derror_input_gain)
        self.dcontrol_output_gain = float(dcontrol_output_gain)
        self.last_error_percent = 0.0
        self.last_control_action = 0.0
        self.input_mfs = {
            'NL': {'points': [-np.inf, -10, -5]}, 'NS': {'points': [-10, -5, 0]},
            'ZE': {'points': [-5, 0, 5]}, 'PS': {'points': [0, 5, 10]},
            'PL': {'points': [5, 10, np.inf]}
        }
        self.output_singletons = {
            'NL': -5.0, 'NS': -2.5, 'ZE': 0.0, 'PS': 2.5, 'PL': 5.0
        }
        self.rule_base = [
            ['NL', 'NL', 'NL', 'NS', 'ZE'], ['NL', 'NL', 'NS', 'ZE', 'PS'],
            ['NL', 'NS', 'ZE', 'PS', 'PL'], ['NS', 'ZE', 'PS', 'PL', 'PL'],
            ['ZE', 'PS', 'PL', 'PL', 'PL']
        ]
        self.mf_names = ['NL', 'NS', 'ZE', 'PS', 'PL']

    def _fuzzify(self, crisp_value: float) -> dict:
        memberships = {}
        for name, mf in self.input_mfs.items():
            p = mf['points']
            mu = 0.0
            if p[0] == -np.inf and crisp_value <= p[2]:
                mu = 1.0 if crisp_value <= p[1] else (p[2] - crisp_value) / (p[2] - p[1])
            elif p[2] == np.inf and crisp_value >= p[0]:
                mu = 1.0 if crisp_value >= p[1] else (crisp_value - p[0]) / (p[1] - p[0])
            elif p[0] <= crisp_value <= p[1]:
                mu = (crisp_value - p[0]) / (p[1] - p[0])
            elif p[1] < crisp_value <= p[2]:
                mu = (p[2] - crisp_value) / (p[2] - p[1])
            memberships[name] = mu
        return memberships

    def _calculate_fuzzy_output(self, scaled_error: float, scaled_derror: float) -> float:
        mu_e = self._fuzzify(scaled_error)
        mu_de = self._fuzzify(scaled_derror)
        numerator, denominator = 0.0, 0.0
        for e_idx, e_name in enumerate(self.mf_names):
            for de_idx, de_name in enumerate(self.mf_names):
                output_mf_name = self.rule_base[e_idx][de_idx]
                output_singleton_val = self.output_singletons[output_mf_name]
                firing_strength = min(mu_e[e_name], mu_de[de_name])
                if firing_strength > 0:
                    numerator += firing_strength * output_singleton_val
                    denominator += firing_strength
        return numerator / denominator if denominator != 0 else 0.0

    def step(self, buffers_dict: dict) -> ControlResult:
        buffer_vals_percent = [b.get_occupancy_as_percent() for b in buffers_dict.values() if b.running]
        if buffer_vals_percent:
            current_occupancy_percent = np.mean(buffer_vals_percent)
            error_percent = self.setpoint - current_occupancy_percent
            derror_percent = error_percent - self.last_error_percent
            scaled_e = error_percent * self.error_input_gain
            scaled_de = derror_percent * self.derror_input_gain
            delta_control_base = self._calculate_fuzzy_output(scaled_e, scaled_de)
            delta_control = delta_control_base * self.dcontrol_output_gain
            control_action = self.last_control_action + delta_control
            self.last_error_percent = error_percent
            self.last_control_action = control_action
        else:
            control_action = self.last_control_action
        return ControlResult(freq_correction=control_action, do_tick=True)

    def get_control(self) -> float:
        return self.last_control_action