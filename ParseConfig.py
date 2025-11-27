import json
from Controllers.TriggeredReframer import TriggeredReframer
from Controllers.PIDControl import PIDController
from Controllers.Reframer import Reframer
from Controllers.FFP import FFP
from Node import Node
from dataclasses import dataclass
from Interchangers import PIDFFP
from Interchangers import ReframingInterchanger
from Controllers.Lag import LagController

@dataclass
class BufferSettings:
    size : int
    initialOcc : int
    localNode : str
    remoteNode : str

@dataclass
class LinkSettings:
    sourceNode : str
    destNode : str
    destInitialOcc : int
    destCapacity : int
    delay : float

def form_controller_from_config(ctrl_opts, nodes, nj):
    controller_type = str(ctrl_opts["type"]).upper()
    if controller_type == "PID":
        controller = PIDController(nj["id"], nodes[nj["id"]], float(ctrl_opts["kp"]), float(ctrl_opts["ki"]), 
                                int(ctrl_opts["ki_window"]), float(ctrl_opts["kd"]), 
                                int(ctrl_opts["diff_step"]), float(ctrl_opts["offset"]))
    elif controller_type == "REFRAMER":
        controller = Reframer(nj["id"], nodes[nj["id"]], float(ctrl_opts["kp"]),
                            float(ctrl_opts["settle_time"]),  float(ctrl_opts["settle_distance"]), float(ctrl_opts["wait_time"]))
    elif controller_type == "INTERCHANGEREFRAMER":
        controller = TriggeredReframer(nj["id"], nodes[nj["id"]], float(ctrl_opts["kp"]),
                            float(ctrl_opts["settle_time"]),  float(ctrl_opts["settle_distance"]), float(ctrl_opts["wait_time"]))
    elif controller_type == "FFP":
        controller = FFP(nj["id"], nodes[nj["id"]])
    elif controller_type == "LAG":
        controller = LagController(nj["id"], nodes[nj["id"]], float(ctrl_opts["kp"]), float(ctrl_opts["ki"]), 
                                float(ctrl_opts["kd"]),float(ctrl_opts["lag_kp"]),float(ctrl_opts["lag_td"]),
                                float(ctrl_opts["lead_kp"]),float(ctrl_opts["lead_td"]))

    else:
        print("Unknown control scheme " + str(ctrl_opts["type"]))
        exit(0)
    return controller
    

def load_nodes_from_config(path, serv):

    nodes = {}
    links = {}
    
    with open(path, 'r') as conf:
        config_json = json.load(conf)
        nodes_json = config_json["nodes"]
        links_json = config_json["links"]

        for nj in nodes_json:
            buffer_configs = nj["buffers"]
            all_buffs = [] #remote buffer : buff
            for buffer in buffer_configs:
                all_buffs.append(
                    BufferSettings(int(buffer["capacity"]),
                                    int(buffer["initial_occ"]),
                                    nj["id"],
                                    buffer["dst_label"]))
            
            for link in links_json:
                source_id = link["source_id"]
                if source_id != nj["id"]: continue
                links[source_id] = {}
                for destination in link["destinations"]:
                    #find destination buffer info
                    for nd in nodes_json:
                        if nd["id"] != destination['dest_node_id']: continue
                        for dest_buffer in nd["buffers"]:
                            if dest_buffer["dst_label"] == source_id:
                                remote_starting_occ = dest_buffer["initial_occ"]
                                remote_max_occ = dest_buffer["capacity"]
                                break
                            else:
                                continue
                        
                        links[source_id][destination["dest_node_id"]] = LinkSettings(source_id, destination["dest_node_id"],  
                                                                                                int(remote_starting_occ),
                                                                                                int(remote_max_occ),
                                                                                                float(destination["delay"]))
            nodes[nj["id"]] = Node(nj["id"], all_buffs, float(nj["frequency"]), server=serv, outgoing_links=links[nj["id"]])
            if "max_frequency" in nj:
                nodes[nj["id"]].maxFreq = float(nj["max_frequency"])
            
            #check if this is a controller config, or a runtime interchange config:
            
            if "interchange" in nj:
                interchange_type = nj["interchange"]
                if (str(interchange_type).upper() == "PIDFFP"):
                    interchanger = PIDFFP.PIDFFP("PIDFFP")
                elif (str(interchange_type).upper() == "ROBUST"):
                    interchanger = ReframingInterchanger.REFRAMING_INTERCHANGER("ROBUST")
                else:
                    print("Unknown interchanger scheme " + interchange_type)
                    exit(0)
                nodes[nj["id"]].set_runtime_interchanger(interchanger)
                controllers_cfg = nj["controller_bank"]
                for controller_cfg in controllers_cfg:
                    controller = form_controller_from_config(controller_cfg, nodes, nj)
                    controller_name = controller_cfg["name"]
                    interchanger.register_controller(controller_name, controller)
            elif "controller" in nj:
                ctrl_opts = nj["controller"]
                controller = form_controller_from_config(ctrl_opts, nodes, nj)
                nodes[nj["id"]].set_controller(controller)
                
            
    return (nodes, links)