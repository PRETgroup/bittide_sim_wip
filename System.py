from operator import attrgetter
from ControlServer import ControlServer
from progress.bar import IncrementalBar
import argparse
from Plotter import Plotter
from ParseConfig import load_nodes_from_config

class BackPressureMessage():
    def __init__(self, destNode, destTime, timestamp):
        self.destNode = destNode
        self.destTime = destTime
        self.timestamp=timestamp

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
        next_steps[node] = 1 / nodes[node].freq
    waiting_messages = []
    backpressure_messages = [] # only used for modelling FFP isFull behavrious

    plotter = Plotter(nodes, links)
    next_graph = 0.0

    if serv is not None:
        serv.handle_fsm_connections(plotter.node_labels)

    # main body
    bar = IncrementalBar('Running', fill='@', suffix='%(percent)d%%')
    while t <= end_t:
        for i, message in enumerate(waiting_messages):
            if message.destTime <= t:
                nodes[message.destNode].buffer_receive(message.destBuffer, message.value)
                waiting_messages.remove(message)

        for i, message in enumerate(backpressure_messages):
            if message.destTime <= t:
                nodes[message.destNode].backpressure_update(message.timestamp)
                backpressure_messages.remove(message)

        for node in nodes.values():
            if next_steps[node.name] <= t:
                out = node.step()
                next_steps[node.name] += out.nextStep
                
                for outgoing_link in links[node.name]:
                    link = links[node.name][outgoing_link]
                    backpressure_messages.append(BackPressureMessage(link.destNode, t + link.delay, out.phase))
                    if out.messages != None:
                        waiting_messages.append(WaitingMessage(link.destNode, link.destBuffer, t + link.delay, out.messages))

        # graph at a lower resolution than the simulation # 
        if next_graph <= t:
            plotter.plot(t)
            next_graph += graph_step

        nextStep = min(next_steps[min(next_steps,key=next_steps.get)], next_graph)
        if len(waiting_messages) > 0:
            nextMessage = min(waiting_messages, key=attrgetter('destTime'))
            t = min(nextStep, nextMessage.destTime)
        else:
            t = nextStep
        bar.goto((int)(t/end_t * 100.0))
    bar.finish()
    
    # graphing 
    throughput_sum = 0.0
    for node in nodes.values():
        print("Node " + node.name + " throughput:")
        print(str(node.phase) + " ticks over " + str(t) + " time units = " + str(node.phase/t) + " ticks per unit")
        throughput_sum += node.phase/t
    print("Average system throughput: " + str(throughput_sum / len(nodes)) + " ticks per unit")
    plotter.render()

    