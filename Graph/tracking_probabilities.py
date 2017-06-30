import networkx as nx
import pickle
import matplotlib.pyplot as plt
import numpy as np


# Return true if a hyperlink edge exists between the nodes and false otherwise
def hyperlink_exists(node, neighbor):
    try:
        edges = G[node][neighbor]
    except KeyError:
        return False

    for edge in edges:
        if edges[edge]['type'] == 'hyperlink':
            return True
    return False


if __name__ == '__main__':
    print("Reading graph file")
    G = pickle.load(open('induced.graph', 'rb'))
    hyperlinks = 0
    tracking = 0

    for i, node in enumerate(G):
        if i % 10000 == 0:
            print("Processed {} nodes".format(i))
            print("Found {} hyperlinks and {} tracking edges.".format(hyperlinks, tracking))
        for neighbor in G[node]:
            edges = G[node][neighbor]
            amt_edges = len(edges)
            if amt_edges == 1 and edges[0]['type'] == 'hyperlink':
                hyperlinks += 1
            elif amt_edges > 1:
                if hyperlink_exists(node, neighbor):
                    for edge in edges:
                        if edges[edge]['type'] == 'hyperlink':
                            hyperlinks += 1
                        else:
                            tracking += 1

    print("Total hyperlinks found:", hyperlinks)
    print("Amount of which also shared tracking:", tracking)