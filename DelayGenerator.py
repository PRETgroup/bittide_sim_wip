from math import pi, sin
import matplotlib.pyplot as plt

from numpy import linspace
import numpy as np

class DelayGenerator:
    def __init__(self, jitter_size, jitter_frequency, spike_size, spike_width, spike_period, delay_size, delay_start):
        self.jitter_size = jitter_size
        self.jitter_frequency = jitter_frequency
        self.spike_size = spike_size
        self.spike_width = spike_width
        self.spike_period = spike_period
        self.delay_size = delay_size
        self.delay_start = delay_start
    
    def get_delay(self,time):
        jitter = self.jitter_size * sin((2 * pi * self.jitter_frequency) * time)
        spike = self.spike_size if ((time+self.spike_width) % self.spike_period) < self.spike_width else 0
        delay = self.delay_size if (time > self.delay_start) else 0
        return jitter+spike+delay
    
if __name__ == "__main__":
    myDelay = DelayGenerator(jitter_size=0.01,jitter_frequency=0.1,spike_size=0.2,spike_width=0.01,spike_period=350,delay_size=0,delay_start=70)
    time_range = linspace(0,600,num=1000000)
    midpoint_freq = lambda t : 0.2 + myDelay.get_delay(t)
    vfunc = np.vectorize(midpoint_freq)
    yvals = vfunc(time_range)
    plt.plot(time_range,yvals,linewidth=1)
    plt.ylim((0,0.6))
    plt.xlim((0,600))
    plt.show()