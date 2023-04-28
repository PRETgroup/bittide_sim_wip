import matplotlib.pyplot as plt
class Plotter:
    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links
        self.node_labels = []
        self.buffer_labels = []
        
        for node in nodes.values():
            self.node_labels.append(node.name)
            for j in range(len(node.get_occupancies())):
                self.buffer_labels.append(node.name + "->" + nodes[links[node.name][j].destNode].name)
        self.timesteps = []
        self.node_frequencies = []
        self.control_outputs = []
        self.buffer_occupancies = []
        self.logical_delay = []

    def plot(self,t):
        step_frequencies = []
        step_outputs = []
        step_occupancies = []
        step_delays = []
        for node in self.nodes.values():
            step_frequencies.append(node.get_frequency())
            step_outputs.append(node.get_control_value())
            step_occupancies.extend(node.get_occupancies_as_percent())
            step_delays.extend(node.get_logical_delays())
        self.timesteps.append(t)
        self.node_frequencies.append(step_frequencies)
        self.control_outputs.append(step_outputs)
        self.buffer_occupancies.append(step_occupancies)
        self.logical_delay.append(step_delays)
    def render(self):
        plt.figure(figsize=(4, 2), dpi=320)
        plt.subplot(2, 1, 1)
        #plt.title("Frequency")
        #plt.ylabel("Hz")
        plt.plot(self.timesteps, self.node_frequencies, label=self.node_labels)
        
        # plt.subplot(4, 1, 2)
        # plt.title("Control Values")
        # plt.ylabel("Hz")
        # plt.plot(timesteps, control_outputs, label=node_labels)
        
        # plt.legend(loc='best')
        # plt.subplot(3, 1, 3)
        # plt.title("Logical Delays")
        # plt.ylabel("Ticks")
        # plt.plot(self.timesteps, self.logical_delay, label=self.buffer_labels)

        plt.legend(loc='best')
        plt.subplot(2, 1, 2)
        plt.title("Buffer Occupancies")
        plt.ylabel("Percent")
        plt.plot(self.timesteps, self.buffer_occupancies, label=self.buffer_labels)

        plt.ylim(0,100)
        # plt.legend(loc='best')

        plt.show()
