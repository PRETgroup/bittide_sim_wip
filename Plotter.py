import matplotlib.pyplot as plt
class Plotter:
    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links
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
        step_outputs = []
        step_occupancies = []
        step_delays = []
        step_jitter = []
        step_latencies = []
        for node in self.nodes.values():
            step_jitter.append(node.last_jitter)
            step_latencies.extend(node.get_latencies())
            step_frequencies.append(node.get_frequency())
            step_outputs.append(node.get_control_value())
            step_occupancies.extend(node.get_occupancies_as_percent())
            step_delays.extend(node.get_logical_delays())
        self.timesteps.append(t)
        self.jitter.append(step_jitter)
        self.node_frequencies.append(step_frequencies)
        self.control_outputs.append(step_outputs)
        self.buffer_occupancies.append(step_occupancies)
        self.buffer_latencies.append(step_latencies)
        self.logical_delay.append(step_delays)
    def render(self):
        plt.figure(figsize=(4, 2), dpi=160)
        plt.subplot(2, 1, 1)
        plt.title("Frequency")
        plt.ylabel("Hz")
        plt.plot(self.timesteps, self.node_frequencies, label=self.node_labels)

        plt.legend(loc='best')
        plt.subplot(2, 1, 2)
        plt.title("Buffer Occupancies")

        tnrfont = {'fontname':'Times New Roman'}

        plt.ylabel("Percent Occ. ")
        plt.xlabel("firing count")
        plt.plot(self.timesteps, self.buffer_occupancies, label=self.buffer_labels,alpha=0.7)
        plt.xticks(fontproperties='Times New Roman', size=10)
        plt.yticks(fontproperties='Times New Roman', size=10)
        plt.legend(fontsize=8,loc='lower right',ncol=2, frameon=False, borderpad=0,labelspacing=0)

        plt.show()
