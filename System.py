from operator import attrgetter
from ControlServer import ControlServer
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar
import argparse
from ParseConfig import load_nodes_from_config

class WaitingMessage():
    def __init__(self, destNode, destBuffer, destTime, value):
        self.destNode = destNode
        self.destBuffer = destBuffer
        self.destTime = destTime
        self.value = value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run bittide execution simulation')
    parser.add_argument('--conf', help='config file path', required=True)
    parser.add_argument('--graph_step', dest="graph_step", help='Graphing intervals', default=0.001, type=float)
    parser.add_argument('--duration', dest="duration", help='Simulation duration in sim time', default=1, type=float)
    parser.add_argument('--disable_app', action='store_true', help='Simulate the control system without an attached app')
    args = parser.parse_args()
    graph_step = args.graph_step
    end_t = args.duration
    
    if not args.disable_app:
        serv = ControlServer(50000)
    else:
        serv = None
    nodes, links = load_nodes_from_config(args.conf, serv)

    t = 0.0
    next_steps = {}
    for node in nodes:
        next_steps[node] = 0.0
    waiting_messages = []

    node_labels = []
    buffer_labels = []
    for node in nodes.values():
        node_labels.append(node.name)
        for j in range(len(node.get_occupancies())):
            buffer_labels.append(node.name + "->" + nodes[links[node.name][j].destNode].name)

    next_graph = 0.0
    timesteps = []
    node_frequencies = []
    control_outputs = []
    buffer_occupancies = []
    if serv is not None:
        serv.handle_fsm_connections(node_labels)

    bar = IncrementalBar('Running', fill='@', suffix='%(percent)d%%')
    while t <= end_t:
        #print("Running timestep", t)

        for i, message in enumerate(waiting_messages):
            if message.destTime <= t:
                nodes[message.destNode].buffer_receive(message.destBuffer, message.value)
                waiting_messages.remove(message)

        for node in nodes.values():
            if next_steps[node.name] <= t:
                out = node.step()
                next_steps[node.name] += out.nextStep

                for j, value in enumerate(out.messages):
                    link = links[node.name][j]
                    waiting_messages.append(WaitingMessage(link.destNode, link.destBuffer, t + link.delay, value))

        if next_graph <= t:
            step_frequencies = []
            step_outputs = []
            step_occupancies = []
            for node in nodes.values():
                step_frequencies.append(node.get_frequency())
                step_outputs.append(node.get_control_value())
                step_occupancies.extend(node.get_occupancies_as_percent())

            next_graph += graph_step
            timesteps.append(t)
            node_frequencies.append(step_frequencies)
            control_outputs.append(step_outputs)
            buffer_occupancies.append(step_occupancies)
        nextStep = min(next_steps[min(next_steps,key=next_steps.get)], next_graph)
        if len(waiting_messages) > 0:
            nextMessage = min(waiting_messages, key=attrgetter('destTime'))
            t = min(nextStep, nextMessage.destTime)
        else:
            t = nextStep
        bar.goto((int)(t/end_t * 100.0))
    bar.finish()
    

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.title("Frequency")
    plt.ylabel("Hz")
    plt.plot(timesteps, node_frequencies, label=node_labels)

    plt.subplot(3, 1, 2)
    plt.title("Control Values")
    plt.ylabel("Hz")
    plt.plot(timesteps, control_outputs, label=node_labels)
        
    plt.legend(loc='best')
    plt.subplot(3, 1, 3)
    plt.title("Buffer Occupancies")
    plt.ylabel("Percent")
    plt.plot(timesteps, buffer_occupancies, label=buffer_labels)
        
    plt.ylim(0,100)
    plt.legend(loc='best')

    plt.show()
    