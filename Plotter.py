from enum import Enum
import matplotlib.pyplot as plt
# We need to import DelayGenerator to use its type hint for clarity
from DelayGenerator import DelayGenerator 

class Plotter:
    class PlotType(Enum):
        FullSize = 1
        Compact = 2

    def __init__(self, nodes, links, fastest_freq, slowest_freq):
        self.mode = self.PlotType.FullSize
        self.nodes = nodes
        self.links = links
        self.fastest_freq = fastest_freq
        self.slowest_freq = slowest_freq
        self.node_labels = []
        self.buffer_labels = []
        
        for node in nodes.values():
            self.node_labels.append(node.name)
            for link in links[node.name]:
                self.buffer_labels.append(node.name + "->" + links[node.name][link].destNode)
        
        self.timesteps = []
        self.node_frequencies = []
        self.buffer_occupancies = []
        self.buffer_latencies = []
        # NEW: List to store the delay generator's output
        self.generated_delays = []
        self.jitter = []

    # MODIFIED: Added 'delay_generator' parameter
    def plot(self, t: float, delay_generator: DelayGenerator):
        step_frequencies = []
        step_occupancies = []
        step_latencies = []
        
        for node in self.nodes.values():
            step_latencies.extend(node.get_latencies()) 
            step_frequencies.append(node.get_frequency())
            step_occupancies.extend(node.get_occupancies_as_percent())
        
        self.timesteps.append(t)
        self.node_frequencies.append(step_frequencies)
        self.buffer_occupancies.append(step_occupancies)
        self.buffer_latencies.append(step_latencies)
        # NEW: Get and store the current delay from the generator
        self.generated_delays.append(delay_generator.get_delay(t))

    def render(self):
        if not self.timesteps:
            print("No data to plot.")
            return

        if self.mode == self.PlotType.FullSize:
            # MODIFIED: Changed from 3 to 4 subplots
            fig, axs = plt.subplots(4, 1, figsize=(12, 10), dpi=160, sharex=True)
            fig.suptitle("System Analysis", fontsize=16)

            # --- Plot 1: Frequency ---
            axs[0].set_title("Node Frequency")
            axs[0].set_ylabel("Hz")
            axs[0].plot(self.timesteps, self.node_frequencies)
            axs[0].legend(self.node_labels, loc='best')
            axs[0].grid(True, linestyle='--', alpha=0.6)
            axs[0].set_ylim(bottom=170, top=220)

            # --- Plot 2: Buffer Occupancies ---
            axs[1].set_title("Buffer Occupancies")
            axs[1].set_ylabel("Percent Full (%)")
            axs[1].plot(self.timesteps, self.buffer_occupancies, alpha=0.8)
            axs[1].legend(self.buffer_labels, loc='best', fontsize=8, ncol=3)
            axs[1].set_ylim([30, 70])
            axs[1].grid(True, linestyle='--', alpha=0.6)

            # --- Plot 3: Measured Network Latency ---
            axs[2].set_title("Measured Network Latency (End-to-End)")
            axs[2].set_ylabel("Latency (s)")
            axs[2].plot(self.timesteps, self.buffer_latencies, alpha=0.8)
            axs[2].legend(self.buffer_labels, loc='best', fontsize=8, ncol=3)
            axs[2].grid(True, linestyle='--', alpha=0.6)
            axs[2].set_ylim(bottom=0)

            # --- NEW PLOT 4: Delay Generator Output ---
            axs[3].set_title("Delay Generator Output")
            axs[3].set_ylabel("Injected Delay (s)")
            axs[3].set_xlabel("Time (s)")
            axs[3].plot(self.timesteps, self.generated_delays, color='red', label="Generated Delay")
            axs[3].legend(loc='best')
            axs[3].grid(True, linestyle='--', alpha=0.6)
            axs[3].set_ylim(bottom=0)
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])

        elif self.mode == self.PlotType.Compact:
            pass
        
        plt.show()