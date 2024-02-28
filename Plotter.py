from enum import Enum
import matplotlib.pyplot as plt
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
                self.buffer_labels.append(links[node.name][link].destNode + "->" + node.name)
        self.timesteps = []
        self.node_frequencies = []
        self.control_outputs = []
        self.buffer_occupancies = []
        self.logical_delay = []
        self.buffer_latencies = []
        self.jitter = []

    def plot(self,t):
        step_frequencies = []
        step_occupancies = []
        step_delays = []
        step_jitter = []
        step_latencies = []
        for node in self.nodes.values():
            step_jitter.append(node.last_jitter)
            step_latencies.extend(node.get_latencies())
            step_frequencies.append(node.get_frequency())
            step_occupancies.extend(node.get_occupancies_as_percent())
            step_delays.extend(node.get_logical_delays())
        self.timesteps.append(t)
        self.jitter.append(step_jitter)
        self.node_frequencies.append(step_frequencies)
        self.buffer_occupancies.append(step_occupancies)
        self.buffer_latencies.append(step_latencies)
        self.logical_delay.append(step_delays)
    def render(self):

        if self.mode == self.PlotType.FullSize:
            plt.figure(figsize=(4, 2), dpi=160)
            plt.subplot(2, 1, 1)
            plt.title("Frequency")
            plt.ylabel("Hz")
            plt.plot(self.timesteps, self.node_frequencies, label=self.node_labels)
            plt.ylim([self.slowest_freq/1.01,self.fastest_freq*1.01])
            plt.legend(loc='best')
            plt.subplot(2, 1, 2)
            plt.title("Buffer Occupancies")

            tnrfont = {'fontname':'Times New Roman'}

            plt.ylabel("Percent Occ. ")
            plt.xlabel("firing count")
            plt.plot(self.timesteps, self.buffer_occupancies, label=self.buffer_labels,alpha=0.7)
            plt.ylim([0,100])
            plt.xticks(fontproperties='Times New Roman', size=10)
            plt.yticks(fontproperties='Times New Roman', size=10)
            plt.legend(fontsize=8,loc='lower right',ncol=2, frameon=False, borderpad=0,labelspacing=0)
        elif self.mode == self.PlotType.Compact:
            #render freq and occ in separate windows
            pass

        plt.show()
