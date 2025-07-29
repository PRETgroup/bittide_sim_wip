import json
from Controllers.TriggeredReframer import TriggeredReframer
from Controllers.PIDControl import PIDController
from Controllers.Reframer import Reframer
from Controllers.FFP import FFP
from Node import Node # Assuming Node.py is in a location accessible by this import
from dataclasses import dataclass
from Interchangers import PIDFFP
from Interchangers import ReframingInterchanger
from Controllers.Lag import LagController
from Controllers.FuzzyPController import FuzzyPController
from DelayGenerator import DelayGenerator 

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
    # MODIFICATION: Changed 'delay : float' to 'delay_model : DelayGenerator'
    delay_model : DelayGenerator # This will now store an instance of DelayGenerator

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

    elif controller_type == "FUZZYP": #Add Fuzzy P controller logic
       
        controller = FuzzyPController(
            name=nj["id"],
            node=nodes[nj["id"]],
            setpoint=float(ctrl_opts.get("setpoint", 50.0)),
            error_input_gain=float(ctrl_opts.get("error_input_gain", 0.2)),
            control_output_gain=float(ctrl_opts.get("control_output_gain", -1.5))
        )
        


    else:
        print("Unknown control scheme " + str(ctrl_opts["type"]))
        exit(0)
    return controller
    

def load_nodes_from_config(path, serv):
    nodes = {}
    # links is a dictionary where keys are source_node_id and 
    # values are dictionaries of {dest_node_id: LinkSettings_instance}
    links = {} 
    
    with open(path, 'r') as conf:
        config_json = json.load(conf)
        nodes_json = config_json["nodes"]
        links_json = config_json["links"]

        for nj in nodes_json: # Iterate over each node definition in the JSON
            buffer_configs = nj["buffers"]
            all_buffs = [] 
            for buffer_conf in buffer_configs: # Corrected variable name from 'buffer' to 'buffer_conf'
                all_buffs.append(
                    BufferSettings(int(buffer_conf["capacity"]),
                                   int(buffer_conf["initial_occ"]),
                                   nj["id"],
                                   buffer_conf["dst_label"]))
            
            # This part processes links that originate from the current node 'nj'
            for link_group_info in links_json: # Iterates over the main "links" array from JSON
                source_id_in_link_group = link_group_info["source_id"]
                
                if source_id_in_link_group == nj["id"]: # We are processing links for the current node nj
                    if nj["id"] not in links:
                        links[nj["id"]] = {} # Initialize dict for this source node's links

                    for destination_info in link_group_info["destinations"]:
                        dest_node_id = destination_info["dest_node_id"]
                        
                        # Find destination buffer info (remote_starting_occ, remote_max_occ)
                        # This part looks for the buffer on the destination node that is designated for traffic from nj["id"]
                        remote_starting_occ_val = None
                        remote_max_occ_val = None
                        found_dest_buffer = False
                        for dest_node_candidate_info in nodes_json:
                            if dest_node_candidate_info["id"] == dest_node_id:
                                for dest_buffer_on_dest_node in dest_node_candidate_info["buffers"]:
                                    if dest_buffer_on_dest_node["dst_label"] == nj["id"]: # dst_label points back to source
                                        remote_starting_occ_val = dest_buffer_on_dest_node["initial_occ"]
                                        remote_max_occ_val = dest_buffer_on_dest_node["capacity"]
                                        found_dest_buffer = True
                                        break
                                if found_dest_buffer:
                                    break
                        
                        if not found_dest_buffer:
                            print(f"ERROR: Configuration error. Could not find buffer information on destination node '{dest_node_id}' for link from '{nj['id']}'. Skipping link.")
                            continue

                        # --- MODIFICATION START: Process delay information ---
                        current_delay_gen = None
                        if "delay_params" in destination_info:
                            params = destination_info["delay_params"]
                            try:
                                # Ensure spike_period is valid if spikes are enabled
                                spike_period_val = float(params.get("spike_period", 1.0))
                                if spike_period_val <= 0 and float(params.get("spike_size", 0.0)) > 0:
                                    print(f"Warning: 'spike_period' must be > 0 if 'spike_size' > 0 for link {nj['id']}->{dest_node_id}. Defaulting to 1.0.")
                                    spike_period_val = 1.0

                                current_delay_gen = DelayGenerator(
                                    jitter_size=float(params.get("jitter_size", 0.0)),
                                    jitter_frequency=float(params.get("jitter_frequency", 0.1)),
                                    spike_size=float(params.get("spike_size", 0.0)),
                                    spike_width=float(params.get("spike_width", 0.01)),
                                    spike_period=spike_period_val,
                                    min_base_delay=float(params["min_base_delay"]), # Mandatory
                                    max_base_delay=float(params["max_base_delay"]), # Mandatory
                                    delay_start=float(params.get("delay_start", 0.0)),
                                    delay_end=float(params.get("delay_end", 1.0e9)) # Default to a large number
                                )
                            except KeyError as e:
                                print(f"ERROR: Missing mandatory key {e} in 'delay_params' for link {nj['id']}->{dest_node_id}. Skipping link.")
                                continue
                            except ValueError as e: # Handles float conversion errors
                                print(f"ERROR: Invalid numeric value in 'delay_params' for link {nj['id']}->{dest_node_id}: {e}. Skipping link.")
                                continue

                        elif "delay" in destination_info: # Fallback to old fixed delay format
                            fixed_delay = float(destination_info["delay"])
                            current_delay_gen = DelayGenerator(
                                jitter_size=0.0, jitter_frequency=0.1,
                                spike_size=0.0, spike_width=0.01, spike_period=1.0, # spike_period must be > 0
                                min_base_delay=fixed_delay, max_base_delay=fixed_delay,
                                delay_start=0.0, delay_end=1.0e9
                            )
                        else:
                            print(f"WARNING: No delay information ('delay_params' or 'delay') for link {nj['id']}->{dest_node_id}. Defaulting to 0 delay.")
                            current_delay_gen = DelayGenerator(
                                jitter_size=0.0, jitter_frequency=0.1,
                                spike_size=0.0, spike_width=0.01, spike_period=1.0,
                                min_base_delay=0.0, max_base_delay=0.0,
                                delay_start=0.0, delay_end=1.0e9
                            )
                        
                        links[nj["id"]][dest_node_id] = LinkSettings(
                            sourceNode=nj["id"], 
                            destNode=dest_node_id,  
                            destInitialOcc=int(remote_starting_occ_val),
                            destCapacity=int(remote_max_occ_val),
                            delay_model=current_delay_gen # Store the DelayGenerator instance
                        )
                 
            
            # Create Node instance
            # Ensure outgoing_links is a dict; if a node has no outgoing links, provide an empty dict.
            node_outgoing_links = links.get(nj["id"], {}) 
            nodes[nj["id"]] = Node(nj["id"], all_buffs, float(nj["frequency"]), 
                                   server=serv, outgoing_links=node_outgoing_links)
            
            # Controller and Interchanger setup (remains the same)
            if "interchange" in nj:
                interchange_type = nj["interchange"]
                # ... (rest of interchanger logic) ...
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