from Controllers.Controller import Controller
from Buffer import BufferSettings
from Node import Node

from operator import attrgetter
import matplotlib.pyplot as plt

class LinkSettings():
    def __init__(self, destNode, destBuffer, delay):
        self.destNode = destNode
        self.destBuffer = destBuffer
        self.delay = delay

class WaitingMessage():
    def __init__(self, destNode, destBuffer, destTime, value):
        self.destNode = destNode
        self.destBuffer = destBuffer
        self.destTime = destTime
        self.value = value

graph_step = 0.0001
end_t = 0.1

links = {
    0: {
        0: LinkSettings(1, 0, 0.0001),
    },
    1: {
        0: LinkSettings(0, 0, 0.0002),
    },
}

nodes = []
nodes.append(Node("n1", Controller("n1"), [
    BufferSettings(100, 50),
], 1000.0))
nodes.append(Node("n2", Controller("n2"), [
    BufferSettings(100, 50),
], 500.0))

t = 0.0
next_steps = [0.0, 0.0]
waiting_messages = []

node_labels = []
buffer_labels = []
for i, node in enumerate(nodes):
    node_labels.append(node.name)
    for j in range(len(node.get_occupancies())):
        buffer_labels.append(node.name + "->" + nodes[links[i][j].destNode].name)

next_graph = 0.0
timesteps = []
node_frequencies = []
buffer_occupancies = []

while t <= end_t:
    # print("Running timestep", t)

    for i, message in enumerate(waiting_messages):
        if message.destTime <= t:
            nodes[message.destNode].buffer_receive(message.destBuffer, value)
            waiting_messages.remove(message)

    for i, node in enumerate(nodes):
        if next_steps[i] <= t:
            out = node.step()
            next_steps[i] += out.nextStep

            for j, value in enumerate(out.messages):
                link = links[i][j]
                waiting_messages.append(WaitingMessage(link.destNode, link.destBuffer, t + link.delay, value))

    if next_graph <= t:
        step_frequencies = []
        step_occupancies = []
        for node in nodes:
            step_frequencies.append(node.get_frequency())
            step_occupancies.extend(node.get_occupancies_as_percent())

        next_graph += graph_step
        timesteps.append(t)
        node_frequencies.append(step_frequencies)
        buffer_occupancies.append(step_occupancies)

    nextStep = min(min(next_steps), next_graph)
    if len(waiting_messages) > 0:
        nextMessage = min(waiting_messages, key=attrgetter('destTime'))
        t = min(nextStep, nextMessage.destTime)
    else:
        t = nextStep

print("Finished")

plt.figure()
plt.subplot(2, 1, 1)
plt.title("Frequency")
plt.ylabel("Hz")
plt.plot(timesteps, node_frequencies, label=node_labels)
plt.legend(loc='best')
plt.subplot(2, 1, 2)
plt.title("Buffer Occupancies")
plt.ylabel("Percent")
plt.plot(timesteps, buffer_occupancies, label=buffer_labels)
plt.legend(loc='best')

plt.show()