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


class NodeCircle:
    def __init__(self, pos, label, radius, graph):  
        self.figure_id = graph.draw_circle(pos, radius, 'white', 'black', 1)
        self.label_id = graph.draw_text(label, pos)
        self.pos = pos
        self.label = label
        self.radius = radius
        self.kp = 0
        self.ki = 0
        self.ki_win = 20
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
    def __init__(self, node_a, node_b, graph):  
        self.node_a = node_a
        self.node_b = node_b
        self.fig_id = graph.draw_line((node_a.pos[0], node_a.pos[1]), (node_b.pos[0], node_b.pos[1]))
        self.delay = 0
        self.capacity_per_node = 100
        self.initial_occ_per_node = 50
        
    def relocate(self, graph):
        graph.delete_figure(self.fig_id)
        self.fig_id = graph.draw_line((self.node_a.pos[0], self.node_a.pos[1]), (self.node_b.pos[0], self.node_b.pos[1]))
    
    def delete_figure(self, graph):
        graph.delete_figure(self.fig_id)
        
    
def get_nodes_at_location(graph, pos, nodes):
    existing_items = list(graph.get_figures_at_location(pos))
    for item in existing_items:
        if item not in nodes:
            existing_items.remove(item)
    return tuple(existing_items)

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
    col = [[sg.Multiline('', size=(40,25), disabled=True,key = "jsonout")], [sg.Input(default_text="./arch.json",size=(30,1), key="filenameval"),sg.Button('Save')]]
    layout = [[sg.Graph(
        canvas_size=(640, 480),
        graph_bottom_left=(0, 0),
        graph_top_right=(640, 480),
        key="-GRAPH-",
        background_color='lightblue',
        right_click_menu=[[],['Erase', 'Link', 'Edit', ['Freq', 'kp', 'ki', 'ki win', 'kd', 'kd step', 'offset']]],
        drag_submits=True,
        enable_events=True), sg.Col(col,key="JSONOUT")]]

    window = sg.Window("Graph Maker", layout, finalize=True)
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
        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse action
            x, y = values["-GRAPH-"] # get mouse position
            if (state == State.IDLE):
                state = State.DRAGGING
                existing_items = get_nodes_at_location(graph, (x,y), node_circles)
                if(len(existing_items) > 0): #check if we already have a node under our mouse
                    holding = (existing_items[0],node_circles[existing_items[0]])
                else: #otherwise, create one
                    radius = 30
                    label = "n" + str(next_id)
                    new_circle = NodeCircle((x,y),label,radius, graph)
                    node_circles[new_circle.figure_id] = new_circle
                    holding = (new_circle.figure_id,node_circles[new_circle.figure_id])
                    next_id += 1
            elif (state == State.DRAGGING):
                holding[1].relocate(graph, (x,y))
                for link in node_links:
                    if holding[1].figure_id in link:
                        node_links[link].relocate(graph)
                        
            
        if event == "-GRAPH-+UP":
            state = State.IDLE
            
        if event == "Link":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                if(state == State.IDLE):
                    state = State.DRAGGING
                    node_a = node_circles[nodes_at_location[0]]
                elif (state == State.DRAGGING):
                    state = State.IDLE
                    node_b = node_circles[nodes_at_location[0]]  
                    if (node_a != node_b):
                        if (frozenset([node_a.figure_id, node_b.figure_id]) in node_links):
                            node_links[frozenset([node_a.figure_id, node_b.figure_id])].delete_figure(graph)
                            node_links.pop(frozenset([node_a.figure_id,node_b.figure_id]))
                        else:
                            new_link = NodeLinks(node_a, node_b, graph)
                            node_links[frozenset([node_a.figure_id,node_b.figure_id])] = new_link
        if event == "Erase":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                erase_node(graph, node_circles, node_links, node)
        
        #parameter editing FIXME code duplication
        if event == "Freq":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("Frequency value:", default_text=node.frequency)
                if (input_val != None and isfloat(input_val)):
                    node.frequency = float(input_val)
                node.update_text(graph)
        
        if event == "kp":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("kp value:", default_text=node.kp)
                if (input_val != None and isfloat(input_val)):
                    node.kp = float(input_val)
                node.update_text(graph)
                
        if event == "ki":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("ki value:", default_text=node.ki)
                if (input_val != None and isfloat(input_val)):
                    node.ki = float(input_val)
                node.update_text(graph)
        
        if event == "ki win":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("ki win value:", default_text=node.ki_win)
                if (input_val != None and input_val.isnumeric()):
                    node.ki_win = int(input_val)
                node.update_text(graph)
                
        if event == "kd":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("kd value:", default_text=node.kd)
                if (input_val != None and isfloat(input_val)):
                    node.kd = float(input_val)
                node.update_text(graph)
        
        if event == "kd step":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("kd step value:", default_text=node.kd_step)
                if (input_val != None and input_val.isnumeric()):
                    node.kd_step = int(input_val)
                node.update_text(graph)
            
        if event == "offset":
            x, y = values["-GRAPH-"]
            nodes_at_location = get_nodes_at_location(graph, (x,y), node_circles)
            if (len(nodes_at_location) > 0):
                node = node_circles[nodes_at_location[0]]
                input_val = sg.popup_get_text("offset:", default_text=node.ofset)
                if (input_val != None and isfloat(input_val)):
                    node.offset = float(input_val)
                node.update_text(graph)
                
        update_json(node_circles, node_links, json_element)
        if event == "Save":
            file_name = values["filenameval"]
            file_contents = values["jsonout"]
            f = open(file_name, "w")
            f.write(file_contents)
            f.close()

    window.close()
    
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
                "midpoint" : 50,
                "offset" : node_obj.offset
            },
            "buffers" : [],
            "frequency" : node_obj.frequency
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
        #need to be grouped by source
        #one link actually represents two physical links
        both_directions = [list(link), list(link)[::-1]]
        
        for dirLink in both_directions:
            #format link x->y
            #since in our json format all links are grouped by source, we must check if an element already
            #exists with this source (FIXME: change the json format so we don't have to do this)
            src_exists = (False,-1)
            dst_exists = (False,-1)
            for it,source_links in enumerate(links_conf):
                if source_links["source_id"] == nodes[dirLink[0]].label:
                    src_exists = (True, it)
                    break
                
            for it,source_links in enumerate(links_conf):
                if source_links["source_id"] == nodes[dirLink[1]].label:
                    dst_exists = (True, it)
                    break
            
            if (dst_exists[0]):
                dstBuffer = len(links_conf[dst_exists[1]]["destinations"])-1
            else:
                dstBuffer = 0
                
            if (src_exists[0]):
                srcConfig = links_conf[src_exists[1]]
                srcConfig["destinations"].append (
                    {
                        "source_buffer_id" : len(srcConfig["destinations"]),
                        "dest_node_id" : nodes[dirLink[1]].label,
                        "dest_buffer_id" : dstBuffer,
                        "delay" : links[link].delay
                    }
                )
            else:
                links_conf.append(
                    {
                        "source_id" : nodes[dirLink[0]].label,
                        "destinations" : [
                            {
                                "source_buffer_id" : 0,
                                "dest_node_id" : nodes[dirLink[1]].label,
                                "dest_buffer_id" : dstBuffer,
                                "delay" : links[link].delay
                            }
                        ]
                    }
                )
       
    element.Update(disabled = False)
    element.Update(json.dumps(json_content, indent=2))
    element.Update(disabled = True)

if __name__ == "__main__":
    main()