from enum import Enum
import matplotlib.pyplot as plt
class Plotter:
    class PlotType(Enum):
        FullSize = 1
        Compact = 2

    class FrequencyMode(Enum):
        Instantaneous = 1
        Averaged = 2

    def __init__(self, nodes, links, fastest_freq, slowest_freq):
        self.mode = self.PlotType.FullSize
        self.frequency_mode = self.FrequencyMode.Instantaneous
        self.nodes = nodes
        self.links = links
        self.fastest_freq = fastest_freq
        self.slowest_freq = slowest_freq
        self.node_labels = []
        self.buffer_labels = []
        
        for node in nodes.values():
            self.node_labels.append(node.name)
            for link in links[node.name]:
                self.buffer_labels.append(links[node.name][link].destNode + "->" + node.name)
        self.timesteps = []
        self.node_frequencies = []
        self.node_average_frequencies = []
        self.node_average_frequencies_skipped = []
        self.control_outputs = []
        self.buffer_occupancies = []
        self.node_occupancies = []
        self.logical_delay = []
        self.buffer_latencies = []
        self.jitter = []

    def plot(self,t):
        step_frequencies = []
        step_average_frequencies = []
        step_average_frequencies_skipped = []
        step_control_outputs = []
        step_occupancies = []
        step_node_occupancies = []
        step_delays = []
        step_jitter = []
        step_latencies = []
        for node in self.nodes.values():
            step_jitter.append(node.last_jitter)
            step_latencies.extend(node.get_latencies())
            step_frequencies.append(node.get_frequency())
            step_average_frequencies.append(node.get_average_frequency())
            step_average_frequencies_skipped.append(node.get_average_frequency_with_skip())
            step_control_outputs.append(node.controller.get_control())
            step_occupancies.extend(node.get_occupancies_as_percent())
            step_node_occupancies.append(node.get_average_occupancy_as_percent())
            step_delays.extend(node.get_logical_delays())
        self.timesteps.append(t)
        self.jitter.append(step_jitter)
        self.node_frequencies.append(step_frequencies)
        self.node_average_frequencies.append(step_average_frequencies)
        self.node_average_frequencies_skipped.append(step_average_frequencies_skipped)
        self.control_outputs.append(step_control_outputs)
        self.buffer_occupancies.append(step_occupancies)
        self.node_occupancies.append(step_node_occupancies)
        self.buffer_latencies.append(step_latencies)
        self.logical_delay.append(step_delays)
    def render(self):

        if self.mode == self.PlotType.FullSize:
            plt.figure(figsize=(4, 2), dpi=160)
            plt.subplot(3, 1, 1)
            plt.title("Frequency")
            plt.ylabel("Hz")
            if self.frequency_mode == self.FrequencyMode.Instantaneous:
                plt.plot(self.timesteps, self.node_frequencies, label=self.node_labels)
            elif self.frequency_mode == self.FrequencyMode.Averaged:
                plt.plot(self.timesteps, self.node_average_frequencies, label=self.node_labels)
                plt.gca().set_prop_cycle(None)
                plt.plot(self.timesteps, self.node_average_frequencies_skipped, label='_nolegend_', alpha=0.2)
            plt.legend(loc='best')

            plt.subplot(3, 1, 2)
            plt.title("Buffer Occupancies")
            plt.ylabel("Percent Occ. ")
            plt.plot(self.timesteps, self.buffer_occupancies, label=self.buffer_labels,alpha=0.7)
            plt.ylim([0,100])
            plt.legend(loc='best', fontsize=8, ncol=2)

            plt.subplot(3, 1, 3)
            plt.title("Node Average Occupancies")
            plt.ylabel("Percent Occ. ")
            plt.xlabel("firing count")
            plt.plot(self.timesteps, self.node_occupancies, label=self.node_labels)
            plt.ylim([0,100])
            plt.legend(loc='best')

            plt.subplots_adjust(left=0.1,
                    bottom=0.15, 
                    right=0.9, 
                    top=0.85, 
                    wspace=0.4, 
                    hspace=0.8)
        elif self.mode == self.PlotType.Compact:
            #render freq and occ in separate windows
            pass
        
        plt.show()
