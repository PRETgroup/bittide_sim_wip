from cProfile import label
from enum import Enum
from platform import node
from ParseConfig import load_nodes_from_config
import PySimpleGUI as sg
import json

class State(Enum):
    IDLE=1,
    DRAGGING=2,
    LINKING=3
radius = 30

class NodeCircle:
    def __init__(self, pos, label, radius, graph):  
        self.figure_id = graph.draw_circle(pos, radius, 'white', 'black', 1)
        self.label_id = graph.draw_text(label, pos)
        self.pos = pos
        self.label = label
        self.radius = radius
        self.kp = 0
        self.ki = 0
        self.ki_win = 0
        self.kd = 0
        self.kd_step = 1
        self.offset = 0
        self.frequency = 1000
        
        self.text_pos = (self.pos[0] + self.radius*3, self.pos[1])
        self.cfg_text_id = graph.draw_text("", self.text_pos)
        self.update_text(graph)
        
    def relocate(self, graph, pos):
        self.pos = pos
        x,y = pos
        graph.relocate_figure(self.figure_id, x-self.radius, y+self.radius)
        graph.relocate_figure(self.label_id, x-self.radius, y+self.radius)
        graph.relocate_figure(self.cfg_text_id, x-self.radius, y+self.radius)
        self.update_text(graph)
    
    def update_text(self, graph):
        graph.delete_figure(self.cfg_text_id)
        vals_text = "kp:%f\nki:%f\nki win:%d\nkd:%f\nkd step:%d\noffset:%f\nfrequency:%f\n" % (self.kp, self.ki, self.ki_win, self.kd, self.kd_step, self.offset, self.frequency)
        self.text_pos = (self.pos[0] + self.radius*3, self.pos[1])
        self.cfg_text_id = graph.draw_text(vals_text, self.text_pos)
        
    
    def delete_figure(self, graph):
        graph.delete_figure(self.figure_id)
        graph.delete_figure(self.label_id)
        graph.delete_figure(self.cfg_text_id)

class NodeLinks:
    def __init__(self, node_a, node_b, graph, delay):  
        self.node_a = node_a
        self.node_b = node_b
        self.delay = delay
        self.fig_id = graph.draw_line((node_a.pos[0], node_a.pos[1]), (node_b.pos[0], node_b.pos[1]))
        self.cfg_text_id = graph.draw_text("delay: ", (0,0))
        self.update_text(graph)
        self.capacity_per_node = 100
        self.initial_occ_per_node = 50
        
    def relocate(self, graph):
        graph.delete_figure(self.fig_id)
        self.fig_id = graph.draw_line((self.node_a.pos[0], self.node_a.pos[1]), (self.node_b.pos[0], self.node_b.pos[1]))
        self.update_text(graph)

    def update_text(self, graph):
        graph.delete_figure(self.cfg_text_id)
        vals_text = "delay:%f\n" % (self.delay)
        self.text_pos = ((self.node_a.pos[0] + self.node_b.pos[0]) / 2,(self.node_a.pos[1] + self.node_b.pos[1]) / 2)
        self.cfg_text_id = graph.draw_text(vals_text, self.text_pos)
    
    def delete_figure(self, graph):
        graph.delete_figure(self.fig_id)
        graph.delete_figure(self.cfg_text_id)
        

def find_free_id(nodes, next_id):
    match_found = True
    while (match_found):
        match_found = False
        for node in nodes:
            if nodes[node].label == "n"+str(next_id):
                match_found = True
                next_id += 1
                break
    return next_id

def get_nodes_at_location(graph, pos, nodes):
    try:
        all_items = list(graph.get_figures_at_location(pos))
        remaining_items = []
        for item in all_items:
            if item in nodes:
                remaining_items.append(item)
    except:
        return tuple()
    return tuple(remaining_items)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def main():
    node_circles = {}
    node_links = {}
    
    next_id = 0
    
    sg.theme('Dark Blue 3')
    col = [[sg.Multiline('', size=(40,40), disabled=True,key = "jsonout")],
    [sg.InputText(key='save_file', do_not_clear=False, enable_events=True, visible=False),
    sg.FileSaveAs('Save as...', target='save_file',file_types=[('JSON', '.json')],
    initial_folder=".", default_extension=".json"),
    sg.InputText(key='load_file', do_not_clear=False, enable_events=True, visible=False),
    sg.FileBrowse('Load...', target='load_file',file_types=[('JSON', '.json')],
    initial_folder=".")
    ]]
    layout = [[sg.Graph(
        canvas_size=(640, 480),
        graph_bottom_left=(0, 0),
        graph_top_right=(640, 480),
        expand_x = True,
        expand_y = True,
        key="-GRAPH-",
        background_color='lightblue',
        right_click_menu=[[],['Erase', 'Link', 'Edit', ['Freq', 'kp', 'ki', 'ki win', 'kd', 'kd step', 'offset']]],
        drag_submits=True,
        enable_events=True,
        motion_events=True), sg.Col(col,key="JSONOUT")]]

    window = sg.Window("Graph Maker", layout, finalize=True, resizable=True, element_padding=2)
    # get the graph element for ease of use later
    graph = window["-GRAPH-"]  # type: sg.Graph
    graph.bind('<Button-3>', '+RIGHT+')
    holding=(None,None) #key, val
    state = State.IDLE
    json_element = window.find_element("jsonout")
    update_json(node_circles, node_links, json_element)
    while (True):
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "-GRAPH-+MOVE":
            if (state == State.LINKING):
                graph.delete_figure(linking_line)
                linking_line = graph.draw_line(node_a.pos, values["-GRAPH-"])
            else:
                continue

        elif event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse action
            x, y = values["-GRAPH-"] # get mouse position
            if (state == State.IDLE):
                state = State.DRAGGING
                existing_items = get_nodes_at_location(graph, (x,y), node_circles)
                if(len(existing_items) > 0): #check if we already have a node under our mouse
                    holding = (existing_items[0],node_circles[existing_items[0]])
                else: #otherwise, create one
                    label = "n" + str(next_id)
                    new_circle = NodeCircle((x,y),label,radius, graph)
                    node_circles[new_circle.figure_id] = new_circle
                    holding = (new_circle.figure_id,node_circles[new_circle.figure_id])
                    next_id = find_free_id(node_circles , next_id)
            elif (state == State.DRAGGING):
                holding[1].relocate(graph, (x,y))
                for link in node_links:
                    if holding[1].figure_id in link:
                        node_links[link].relocate(graph)
            elif (state == State.LINKING):
                nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
                if (len(nodes_at_location) > 0):
                    state = State.IDLE
                    node_b = node_circles[nodes_at_location[0]]  
                    
                    if (node_a != node_b):
                        if (frozenset([node_a.figure_id, node_b.figure_id]) in node_links):
                            node_links[frozenset([node_a.figure_id, node_b.figure_id])].delete_figure(graph)
                            node_links.pop(frozenset([node_a.figure_id,node_b.figure_id]))
                        else:
                            input_val = float(sg.popup_get_text("link delay:", default_text=0))
                            new_link = NodeLinks(node_a, node_b, graph, input_val)
                            node_links[frozenset([node_a.figure_id,node_b.figure_id])] = new_link
                graph.delete_figure(linking_line)
                        
        elif event == "-GRAPH-+UP":
            state = State.IDLE

            
        elif event == "Link":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                if(state == State.IDLE):
                    state = State.LINKING
                    node_a = node_circles[nodes_at_location[0]]
                    linking_line = graph.draw_line((x,y), (x,y))

        elif event == "Erase":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                erase_node(graph, node_circles, node_links, node)
        
        #parameter editing        
        elif event == "save_file":
            file_name = values["save_file"]
            if (file_name == ""): continue
            file_contents = values["jsonout"]
            f = open(file_name, "w")
            f.write(file_contents)
            f.close()

        elif event == "load_file":
            list_of_node_names = [node for node in node_circles]
            for node in list_of_node_names:
                erase_node(graph, node_circles,node_links,node_circles[node])
                
            file_name = values["load_file"]
            state = State.IDLE
            holding = (None,None)
            node_circles, node_links = load_from_file(graph, file_name)
            next_id = find_free_id(node_circles, next_id)

        handle_dropdown_events(event, values, graph, node_circles)
        update_json(node_circles, node_links, json_element)

    window.close()

def load_from_file(graph, file_name):
    node_temp_circles = {}
    node_temp_links = {}
    with open(file_name) as f:
        json_dict = json.load(f)
        all_nodes_json = json_dict["nodes"]
        x,y = (0,0)
        jump = 50
        label_to_node = {}
        for node_json in all_nodes_json:
            if "meta_x" in node_json:
                x = int(node_json["meta_x"])
            else: x = x + radius
            if "meta_y" in node_json:
                y = int(node_json["meta_y"])
            else: y = y + radius
            label = node_json["id"]
            new_circle = NodeCircle((x,y),label,radius, graph)
            new_circle.frequency = float(node_json["frequency"])
            control_json = node_json["controller"]
            new_circle.kp = float(control_json["kp"])
            new_circle.ki = float(control_json["ki"])
            new_circle.ki_win = int(control_json["ki_window"])
            new_circle.kd = float(control_json["kd"])
            new_circle.kd_step = int(control_json["diff_step"])
            new_circle.offset = float(control_json["offset"])
            node_temp_circles[new_circle.figure_id] = new_circle
            label_to_node[label] = new_circle
            new_circle.update_text(graph)
        all_links_json = json_dict["links"]
        for link_json in all_links_json:
            node_a = label_to_node[link_json["source_id"]]
            dest_jsons = link_json["destinations"]
            for destination in dest_jsons:
                node_b = label_to_node[destination["dest_node_id"]]
                delay = destination["delay"]
                if frozenset([node_a.figure_id,node_b.figure_id]) in node_temp_links:
                    continue
                new_link = NodeLinks(node_a, node_b, graph,delay)
                node_temp_links[frozenset([node_a.figure_id,node_b.figure_id])] = new_link
    return (node_temp_circles, node_temp_links)

def handle_dropdown_events(event, values, graph, node_circles):
    x, y = values["-GRAPH-"]
    nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
    if (len(nodes_at_location) > 0):
        node = node_circles[nodes_at_location[0]]
        if event == "Freq":
            input_val = sg.popup_get_text("Frequency value:", default_text=node.frequency)
            if (input_val != None and isfloat(input_val)):
                node.frequency = float(input_val)
        elif event == "kp":
            input_val = sg.popup_get_text("kp value:", default_text=node.kp)
            if (input_val != None and isfloat(input_val)):
                node.kp = float(input_val)
        elif event == "ki":
            input_val = sg.popup_get_text("ki value:", default_text=node.ki)
            if (input_val != None and isfloat(input_val)):
                node.ki = float(input_val)
        elif event == "ki win":
            input_val = sg.popup_get_text("ki win value:", default_text=node.ki_win)
            if (input_val != None and input_val.isnumeric()):
                node.ki_win = int(input_val)
        elif event == "kd":
            input_val = sg.popup_get_text("kd value:", default_text=node.kd)
            if (input_val != None and isfloat(input_val)):
                node.kd = float(input_val)
        elif event == "kd step":
            input_val = sg.popup_get_text("kd step value:", default_text=node.kd_step)
            if (input_val != None and input_val.isnumeric()):
                node.kd_step = int(input_val)
        elif event == "offset":
            input_val = sg.popup_get_text("offset:", default_text=node.offset)
            if (input_val != None and isfloat(input_val)):
                node.offset = float(input_val)
        node.update_text(graph)

def erase_node(graph, nodes, links, node):
    node.delete_figure(graph)
    
    #erase all links associated with this node
    for other_node in nodes:
        if other_node == node: continue
        if frozenset([node.figure_id, other_node]) in links:
            links[frozenset([node.figure_id, other_node])].delete_figure(graph)
            links.pop(frozenset([node.figure_id,other_node]))
    
    nodes.pop(node.figure_id)

def update_json(nodes, links, element):
    json_content = {
        "nodes": [],
        "links": []
    }
    node_conf = json_content["nodes"]
    
    for node in nodes:
        node_obj = nodes[node]
        basic_node = {
            "id": node_obj.label,
            "controller" : {
                "type" : "PID",
                "kp" : node_obj.kp,
                "ki" : node_obj.ki,
                "ki_window" : node_obj.ki_win,
                "kd" : node_obj.kd,
                "diff_step" : node_obj.kd_step,
                "offset" : node_obj.offset
            },
            "buffers" : [],
            "frequency" : node_obj.frequency,
            "meta_x" : node_obj.pos[0],
            "meta_y" : node_obj.pos[1]
        }
        #add the buffers
        for link in links:
            if (node in link):
                linklst = list(link)
                linklst.remove(node)
                other_node = linklst[0]
                basic_node["buffers"].append(
                    {
                        "dst_label" : nodes[other_node].label,
                        "capacity" : links[link].capacity_per_node,
                        "initial_occ" : links[link].initial_occ_per_node,
                    }
                )
            
        node_conf.append(basic_node)
    
    links_conf = json_content["links"]
    for link in links:
        x,y = tuple(link)
        x_exists = (False,-1)
        y_exists = (False,-1)
        for it,source_links in enumerate(links_conf):
            if source_links["source_id"] == nodes[x].label:
                x_exists = (True, it)
                break
            
        for it,source_links in enumerate(links_conf):
            if source_links["source_id"] == nodes[y].label:
                y_exists = (True, it)
                break
        
        if x_exists[0]:
            x_len = len(links_conf[x_exists[1]]["destinations"])
        else:
            x_len = 0
            
        if y_exists[0]:
            y_len = len(links_conf[y_exists[1]]["destinations"])
        else:
            y_len = 0
            
        xy_link = {
                    "source_buffer_id" : x_len,
                    "dest_node_id" : nodes[y].label,
                    "dest_buffer_id" : y_len,
                    "delay" : links[link].delay
                }
        yx_link = {
                    "source_buffer_id" : y_len,
                    "dest_node_id" : nodes[x].label,
                    "dest_buffer_id" : x_len,
                    "delay" : links[link].delay
                }
        if (x_exists[0]):
            srcConfig = links_conf[x_exists[1]]
            srcConfig["destinations"].append (xy_link)
        else:
            links_conf.append(
                {
                    "source_id" : nodes[x].label,
                    "destinations" : [
                        xy_link
                    ]
                }
            )
        if (y_exists[0]):
            srcConfig = links_conf[y_exists[1]]
            srcConfig["destinations"].append (yx_link)
        else:
            links_conf.append(
                {
                    "source_id" : nodes[y].label,
                    "destinations" : [
                        yx_link
                    ]
                }
            )

    element.Update(disabled = False)
    element.Update(json.dumps(json_content, indent=2))
    element.Update(disabled = True)

if __name__ == "__main__":
    main()