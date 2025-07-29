import math
import random  # Added for random number generation
# Imports for the __main__ example part
# from matplotlib.pylab import plt # Original in image
import matplotlib.pyplot as plt # More standard
from numpy import linspace
import numpy as np

class DelayGenerator:
    def __init__(self, jitter_size, jitter_frequency, 
                 spike_size, spike_width, spike_period, 
                 min_base_delay, max_base_delay,  # Changed from delay_size
                 delay_start, delay_end):        # delay_start/end are for spike occurrence window
        self.jitter_size = jitter_size
        self.jitter_frequency = jitter_frequency
        self.spike_size = spike_size
        self.spike_width = spike_width
        self.spike_period = spike_period
        
        # Store min and max for the random base delay
        self.min_base_delay = min_base_delay
        self.max_base_delay = max_base_delay
        if self.min_base_delay > self.max_base_delay:
            raise ValueError("min_base_delay cannot be greater than max_base_delay")

        # These parameters define the time window during which spikes can occur
        self.delay_start = delay_start
        self.delay_end = delay_end

    def get_delay(self, time):
        # Calculate jitter component
        jitter = self.jitter_size * math.sin(2 * math.pi * self.jitter_frequency * time)
        
        # Calculate spike component
        spike = 0
        # Spikes only occur if spike_size, spike_width, and spike_period are meaningful positive values
        if self.spike_size > 0 and self.spike_width > 0 and self.spike_period > 0:
            # Check if current time is within a spike pulse (repeats every spike_period)
            is_in_spike_pulse = (time % self.spike_period) < self.spike_width
            # Check if current time is within the allowed window for spikes (delay_start to delay_end)
            is_in_spike_window = (time >= self.delay_start) and (time <= self.delay_end) # Inclusive start/end for window
            
            if is_in_spike_pulse and is_in_spike_window:
                spike = self.spike_size
        
        # Generate random base delay component
        # This is the core change: base delay is now a random value in the defined range
        random_base_component = random.uniform(self.min_base_delay, self.max_base_delay)
        
        # Total delay is the sum of components
        total_delay = jitter + spike + random_base_component
        
        # Ensure delay is not negative (e.g., if jitter is large and negative)
        return max(0, total_delay)

# This block is for testing DelayGenerator.py directly.
# It shows how to instantiate the class with the new parameters.
if __name__ == "__main__":

    # Example parameters:
    # Original params for reference from image: 
    # jitter_size=0.01, jitter_frequency=0.1, 
    # spike_size=0.2, spike_width=0.01, spike_period=250, 
    # delay_size=0.2 (now replaced), delay_start=20, delay_end=70

    # New instantiation with min_base_delay and max_base_delay.
    # Let's assume the previous delay_size was 0.2, and we want it to vary randomly
    # between 0.1 and 0.3.
    min_delay_example = 0.0
    max_delay_example = 0.0
    
    # If you want no jitter or spikes for a purely random delay test, set their sizes to 0.
    example_jitter_size = 0.01 
    example_spike_size = 0.2
    # To disable jitter for the test plot: example_jitter_size = 0
    # To disable spikes for the test plot: example_spike_size = 0


    myDelay = DelayGenerator(jitter_size=example_jitter_size, jitter_frequency=0.1, 
                             spike_size=example_spike_size, spike_width=0.01, spike_period=250, 
                             min_base_delay=min_delay_example, max_base_delay=max_delay_example,
                             delay_start=20, delay_end=70)

    time_range = linspace(0, 100, num=1000) # 1000 points for a clearer plot
    
    # Get delay values for each point in time
    # Using a list comprehension is straightforward for this.
    yvals = [myDelay.get_delay(t) for t in time_range]
    
    # The original plotting script had an offset, let's plot the direct output first
    # midpoint_freq = lambda t: 0.2 + myDelay.get_delay(t) # Original in image
    # vfunc = np.vectorize(midpoint_freq) # vectorize works by calling the function for each element
    # yvals = vfunc(time_range)

    plt.figure(figsize=(10, 6))
    plt.plot(time_range, yvals, linewidth=1, label=f'Random Delay ({min_delay_example}-{max_delay_example})')
    
    # Add lines for min and max base delay to visualize the random range clearly if jitter/spikes are off
    if example_jitter_size == 0 and example_spike_size == 0:
        plt.axhline(y=min_delay_example, color='r', linestyle='--', label=f'Min Base Delay ({min_delay_example})')
        plt.axhline(y=max_delay_example, color='g', linestyle='--', label=f'Max Base Delay ({max_delay_example})')

    plt.xlabel("Time")
    plt.ylabel("Generated Delay")
    plt.title("DelayGenerator Output with Random Base Delay")
    plt.legend()
    plt.grid(True)
    # Adjust ylim based on expected output range
    # plt.ylim(min(yvals) - 0.1 * max(1, abs(min(yvals))), max(yvals) + 0.1 * max(1, abs(max(yvals))))
    # Or set a fixed reasonable ylim if you know the approximate range
    expected_min_plot = min_delay_example - example_jitter_size
    expected_max_plot = max_delay_example + example_jitter_size + example_spike_size
    plt.ylim(max(0, expected_min_plot - 0.1), expected_max_plot + 0.1)
    plt.show()