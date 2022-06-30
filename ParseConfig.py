import json

from Controllers.PIDControl import PIDController
from Buffer import BufferSettings
from Node import Node


class LinkSettings():
    def __init__(self, destNode, destBuffer, delay):
        self.destNode = destNode
        self.destBuffer = destBuffer
        self.delay = delay

def load_nodes_from_config(path):

    nodes = {}
    links = {}
    
    with open(path, 'r') as conf:
        config_json = json.load(conf)
        nodes_json = config_json["nodes"]
        for nj in nodes_json:
            ctrl_opts = nj["controller"]
            if str(ctrl_opts["type"]).upper() == "PID":
                buffer_configs = nj["buffers"]
                all_buffs = []
                for buffer in buffer_configs:
                    all_buffs.append(BufferSettings(int(buffer["capacity"]), int(buffer["initial_occ"])))
                    
                nodes[nj["id"]] = (Node(nj["id"],
                            PIDController(nj["id"], float(ctrl_opts["kp"]), float(ctrl_opts["ki"]), int(ctrl_opts["ki_window"]), float(ctrl_opts["kd"]), 
                                          int(ctrl_opts["diff_step"]), int(ctrl_opts["midpoint"]), float(ctrl_opts["offset"])), all_buffs, float(nj["frequency"])))
            else:
                print("Unknown control scheme " + str(ctrl_opts["type"]))
                exit(0)
                
        links_json = config_json["links"]
        for link in links_json:
            source_id = link["source_id"]
            links[source_id] = {}
            for destination in link["destinations"]:
                links[source_id][int(destination["source_buffer_id"])] = LinkSettings(destination["dest_node_id"], int(destination["dest_buffer_id"]), float(destination["delay"]))
                
    return (nodes, links)