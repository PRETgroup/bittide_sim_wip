from cmath import inf
from collections import deque
import random
from ControlServer import ControlServer
from progress.bar import IncrementalBar
import argparse
from DelayGenerator import DelayGenerator
from Plotter import Plotter
from math import floor
from ParseConfig import load_nodes_from_config
from MessageTypes import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run bittide execution simulation')
    parser.add_argument('--conf', help='config file path', required=True)
    parser.add_argument('--graph_step', dest="graph_step", help='Graphing intervals', default=-1, type=float)
    parser.add_argument('--duration', dest="duration", help='Simulation duration in sim time', default=-1, type=float)
    parser.add_argument('--enable_app', action='store_true', help='Simulate the control system with an attached app')
    args = parser.parse_args()
    graph_step = args.graph_step

    end_t = args.duration
    random.seed(a=1, version=2)
    
    if args.enable_app:
        serv = ControlServer(50000)
    else:
        serv = None
 
    nodes, links = load_nodes_from_config(args.conf, serv)

    t = 0.0
    crash = False
    next_steps = {}
    fastest_node_freq = 0
    slowest_node_freq = inf
    for node in nodes:
        next_steps[node] = 1 / nodes[node].freq
        if nodes[node].freq > fastest_node_freq:
            fastest_node_freq = nodes[node].freq
        if nodes[node].freq < slowest_node_freq:
            slowest_node_freq = nodes[node].freq

    if graph_step == -1: #infer a default graph step from node frequencies (2.1x the fastest node)
        graph_step = 1 / (2.0 * fastest_node_freq)

    if end_t == -1: #infer a default duration from node frequencies
        end_t = 100000 / fastest_node_freq
        

    waiting_messages = deque()
    backpressure_messages = [] # only used for modelling FFP isFull behaviours

    plotter = Plotter(nodes, links, fastest_node_freq, slowest_node_freq)
    next_graph = 0.0 # datapoint plotting timer

    if serv is not None: # await networked SCChart, if enabled
        serv.handle_fsm_connections(plotter.node_labels)

    bar = IncrementalBar('Running', fill='@', suffix='%(percent)d%%') #progress bar
    delayGenerator = DelayGenerator(
        jitter_size=0.0,jitter_frequency=0,spike_size=0,spike_width=0.0,spike_period=0,delay_start=500,delay_end=20000, min_base_delay=0.2, max_base_delay=0.5) #modelling various delay attacks
    
    ################################################# main simulation loop
    while t <= end_t and not crash:
        # deliver in-flight messages to receiver
        while(len(waiting_messages) > 0 and waiting_messages[0].destTime <= t):
            message = waiting_messages[0]
            if message.destNode in nodes:
                nodes[message.destNode].buffer_receive(message.sourceNode, message.value)
            waiting_messages.popleft()

        # deliver in-flight backpressure messages (FFP only)
        while(len(backpressure_messages) > 0 and backpressure_messages[0].destTime <= t):
            message = backpressure_messages[0]
            if message.destNode in nodes:
                nodes[message.destNode].backpressure_update(message.sourceNode, message.timestamp)
            backpressure_messages.remove(message)

        # run next node tick(s)
        for node in nodes.values():
            if next_steps[node.name] <= t: #check if tick deadline has expired
                out = node.step(t) #run simulation tick
                if out is None:
                    print("Node " + node.name + " crash at " + str(t))
                    crash = True
                    break
                next_steps[node.name] += out.nextStep #update next tick deadline
                
                for outgoing_link in links[node.name]: #move output messages to outgoing links
                    link = links[node.name][outgoing_link]
                    if out.messages != None:
                        waiting_messages.append(WaitingMessage(link.sourceNode, link.destNode, t + link.delay_model.get_delay(t) + delayGenerator.get_delay(t), out.messages))

                for buffer in node.buffers: #transmit a backpressure message on reverse link (FFP)
                    for link in links[node.buffers[buffer].remoteNode]:
                        if links[node.buffers[buffer].remoteNode][link].destNode == node.name:
                            backpressure_messages.append(BackPressureMessage(node.name,node.buffers[buffer].remoteNode, t + links[node.buffers[buffer].remoteNode][link].delay_model.get_delay(t), node.phase))
                            break

        # graph at a lower resolution than the simulation # 
        if next_graph <= t:
            plotter.plot(t)
            next_graph += graph_step

        #jump the simulation time to the next simulation event (machine tick or message delivery)
        nextStep = min(next_steps[min(next_steps,key=next_steps.get)], next_graph)
        if len(waiting_messages) > 0:
            nextMessage = waiting_messages[0]
            t = min(nextStep, nextMessage.destTime)
        else:
            t = nextStep
        bar.goto((int)(t/end_t * 100.0))
    ################################################
    
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
            responsetime_sum += node.buffers[buffer].latency_sum / node.phase
            print(node.buffers[buffer].latency_sum / node.phase)
    print("Average system throughput: " + str(throughput_sum / len(nodes)) + " ticks per simulated second")
    print("Average point to point latency: " + str(responsetime_sum / len(nodes)) + " ticks per simulated second")
    plotter.render()