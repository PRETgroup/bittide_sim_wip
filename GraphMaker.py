from cProfile import label
from enum import Enum
from platform import node
from ParseConfig import load_nodes_from_config
from Node import Node
import PySimpleGUI as sg

class State(Enum):
    IDLE=1,
    DRAGGING=2,
    LINKING=3


class NodeCircle:
    def __init__(self, pos, figure_id, label, label_id, radius):  
        self.pos = pos
        self.figure_id = figure_id
        self.label = label
        self.label_id = label_id
        self.radius = radius
        self.node = Node(label, None, [], None)
    def relocate(self, graph, pos):
        self.pos = pos
        x,y = pos
        graph.relocate_figure(self.figure_id, x-self.radius, y+self.radius)
        graph.relocate_figure(self.label_id, x-self.radius, y+self.radius)

class NodeLinks:
    def __init__(self, node_a, node_b, fig_id):  
        self.node_a = node_a
        self.node_b = node_b
        self.fig_id = fig_id   
    def relocate(self, graph):
        graph.delete_figure(self.fig_id)
        self.fig_id = graph.draw_line((self.node_a.pos[0], self.node_a.pos[1]), (self.node_b.pos[0], self.node_b.pos[1]))
        
    
def main():
    node_circles = {}
    node_links = {}
    
    next_id = 0
    
    sg.theme('Dark Blue 3')
    col = [[sg.Multiline('', size=(40,25), disabled=True,key = "jsonout")], [sg.Input(default_text="./arch.json",size=(30,1)),sg.Button('Save')]]
    layout = [[sg.Graph(
        canvas_size=(640, 480),
        graph_bottom_left=(0, 0),
        graph_top_right=(640, 480),
        key="-GRAPH-",
        background_color='lightblue',
        right_click_menu=[[],['Erase', 'Link']],
        drag_submits=True,
        enable_events=True), sg.Col(col,key="JSONOUT")]]

    window = sg.Window("Graph Maker", layout, finalize=True)
    # get the graph element for ease of use later
    graph = window["-GRAPH-"]  # type: sg.Graph
    graph.bind('<Button-3>', '+RIGHT+')
    holding=(None,None) #key, val
    state = State.IDLE
    while (True):
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse action
            x, y = values["-GRAPH-"] # get mouse position
            if (state == State.IDLE):
                state = State.DRAGGING
                existing_items = graph.get_figures_at_location((x,y))
                if(len(existing_items) > 0): #check if we already have a node under our mouse
                    holding = (existing_items[0],node_circles[existing_items[0]])
                else: #otherwise, create one
                    radius = 30
                    circle_id = graph.draw_circle((x,y), radius, 'white', 'black', 1)
                    label = "n" + str(next_id)
                    label_id = graph.draw_text(label, (x,y))
                    node_circles[circle_id] = NodeCircle((x,y),circle_id, label, label_id, radius)
                    holding = (circle_id,node_circles[circle_id])
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
            if (len(graph.get_figures_at_location((x,y))) > 0):
                if(state == State.IDLE):
                    state = State.DRAGGING
                    node_a = node_circles[graph.get_figures_at_location((x,y))[0]]
                elif (state == State.DRAGGING):
                    state = State.IDLE
                    node_b = node_circles[graph.get_figures_at_location((x,y))[0]]  
                    if (node_a != node_b):
                        if (frozenset([node_a.figure_id, node_b.figure_id]) in node_links):
                            graph.delete_figure(node_links[frozenset([node_a.figure_id,node_b.figure_id])].fig_id)
                            node_links.pop(frozenset([node_a.figure_id,node_b.figure_id]))
                        else:
                            link_fig_id = graph.draw_line((node_a.pos[0], node_a.pos[1]), (node_b.pos[0], node_b.pos[1]))
                            node_links[frozenset([node_a.figure_id,node_b.figure_id])] = NodeLinks(node_a, node_b, link_fig_id)
        if event == "Erase":
            x, y = values["-GRAPH-"]
            if (len(graph.get_figures_at_location((x,y))) > 0):
                node = node_circles[graph.get_figures_at_location((x,y))[0]]
                erase_node(graph, node_circles, node_links, node)
        
        
        json_element = window.find_element("jsonout")
        json_element.Update(disabled = False)
        update_json(node_circles, node_links, json_element)
        json_element.Update(disabled = True)
    window.close()
    
def erase_node(graph, nodes, links, node):
    graph.delete_figure(node.figure_id)
    graph.delete_figure(node.label_id)
    
    #erase all links associated with this node
    for other_node in nodes:
        if other_node == node: continue
        if frozenset([node.figure_id, other_node]) in links:
            graph.delete_figure(links[frozenset([node.figure_id,other_node])].fig_id)
            links.pop(frozenset([node.figure_id,other_node]))
    
    nodes.pop(node.figure_id)

def update_json(nodes, links, element):
    #element.Update("Hello, World")
    pass

if __name__ == "__main__":
    main()