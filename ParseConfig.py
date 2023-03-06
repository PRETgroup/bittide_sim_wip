import json

from Controllers.PIDControl import PIDController
from Node import Node
from dataclasses import dataclass

@dataclass
class BufferSettings:
    size : int
    initialOcc : int
    localNode : str
    remoteNode : str

@dataclass
class LinkSettings:
    destNode : str
    destBuffer : str
    delay : float

def load_nodes_from_config(path, serv):

    nodes = {}
    links = {}
    
    with open(path, 'r') as conf:
        config_json = json.load(conf)
        nodes_json = config_json["nodes"]
        for nj in nodes_json:
            ctrl_opts = nj["controller"]
            if str(ctrl_opts["type"]).upper() == "PID":
                buffer_configs = nj["buffers"]
                all_buffs = [] #remote buffer : buff
                for buffer in buffer_configs:
                    all_buffs.append(
                        BufferSettings(int(buffer["capacity"]),
                                        int(buffer["initial_occ"]),
                                        nj["id"],
                                        buffer["dst_label"]))
                    
                nodes[nj["id"]] = (Node(nj["id"],
                            PIDController(nj["id"], float(ctrl_opts["kp"]), float(ctrl_opts["ki"]), int(ctrl_opts["ki_window"]), float(ctrl_opts["kd"]), 
                                          int(ctrl_opts["diff_step"]), float(ctrl_opts["offset"])), all_buffs, float(nj["frequency"]), server=serv))
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