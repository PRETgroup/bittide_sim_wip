from collections import deque
from operator import attrgetter
import random
from ControlServer import ControlServer
from progress.bar import IncrementalBar
import argparse
from DelayGenerator import DelayGenerator
from Plotter import Plotter
from ParseConfig import load_nodes_from_config

class BackPressureMessage():
    def __init__(self, sourceNode, destNode, destTime, timestamp):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.destTime = destTime
        self.timestamp=timestamp

class WaitingMessage():
    def __init__(self, sourceNode, destNode, destTime, value):
        self.sourceNode = sourceNode
        self.destNode = destNode
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
    random.seed(a=1, version=2)
    
    if not args.disable_app:
        serv = ControlServer(50000)
    else:
        serv = None
    nodes, links = load_nodes_from_config(args.conf, serv)

    t = 0.0
    next_steps = {}
    for node in nodes:
        next_steps[node] = 1 / nodes[node].freq
    waiting_messages = deque()
    backpressure_messages = [] # only used for modelling FFP isFull behaviours

    plotter = Plotter(nodes, links)
    next_graph = 0.0

    if serv is not None:
        serv.handle_fsm_connections(plotter.node_labels)

    # main body
    bar = IncrementalBar('Running', fill='@', suffix='%(percent)d%%')
    delayGenerator = DelayGenerator(
        jitter_size=0.01,jitter_frequency=0.1,spike_size=0.2,spike_width=0.01,spike_period=350,delay_size=0,delay_start=70)
    while t <= end_t:
        while(len(waiting_messages) > 0 and waiting_messages[0].destTime <= t):
            message = waiting_messages[0]
            nodes[message.destNode].buffer_receive(message.sourceNode, message.value)
            waiting_messages.popleft()

        while(len(backpressure_messages) > 0 and backpressure_messages[0].destTime <= t):
            message = backpressure_messages[0]
            nodes[message.destNode].backpressure_update(message.sourceNode, message.timestamp)
            backpressure_messages.remove(message)

        for node in nodes.values():
            if next_steps[node.name] <= t:
                out = node.step(t)
                next_steps[node.name] += out.nextStep
                
                for outgoing_link in links[node.name]:
                    link = links[node.name][outgoing_link]
                    if out.messages != None:
                        waiting_messages.append(WaitingMessage(link.sourceNode, link.destNode, t + link.delay + delayGenerator.get_delay(t), out.messages))

                for buffer in node.buffers:
                    #get backwards link characteristic
                    for link in links[node.buffers[buffer].remoteNode]:
                        if links[node.buffers[buffer].remoteNode][link].destNode == node.name:
                            backpressure_messages.append(BackPressureMessage(node.name,node.buffers[buffer].remoteNode, t + 
                                                                             links[node.buffers[buffer].remoteNode][link].delay, node.phase))
                            break

        # graph at a lower resolution than the simulation # 
        if next_graph <= t:
            plotter.plot(t)
            next_graph += graph_step

        nextStep = min(next_steps[min(next_steps,key=next_steps.get)], next_graph)
        if len(waiting_messages) > 0:
            nextMessage = waiting_messages[0]
            t = min(nextStep, nextMessage.destTime)
        else:
            t = nextStep
        bar.goto((int)(t/end_t * 100.0))
    bar.finish()
    
    # graphing 
    responsetime_sum =0.0
    throughput_sum = 0.0
    for node in nodes.values():
        print("Node " + node.name + " throughput:")
        print(str(node.phase) + " ticks over " + str(t) + " time units = " + str(node.phase/t) + " ticks per unit")
        throughput_sum += node.phase/t
        for buffer in node.buffers:
            local_id,remote_id = node.buffers[buffer].getId()
            print("Communication " + str(remote_id) + "->" + str(local_id) + " average response time:")
            print(node.buffers[buffer].latency_sum / node.phase)
    print("Average system throughput: " + str(throughput_sum / len(nodes)) + " ticks per unit")
    plotter.render()

    