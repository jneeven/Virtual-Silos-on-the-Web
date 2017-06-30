"""
Create the induced graph as described in the thesis, removing all cookie and script
nodes and replacing them by edges between domains.
"""

import networkx as nx
import pickle
import matplotlib.pyplot as plt
import numpy as np


# Find edge of ntype between n1 and n2 and return it.
def find_correct_edge(n1, n2, ntype):
    try:
        edges = new[n1][n2]
    except KeyError:
        return None

    for edge in edges:
        if edges[edge]['type'] == ntype:
            return edges[edge]
    return None


# Connect all neighbours of a cookie or script node with the correct edge
def connect_neighbours(node, ntype):
    neighbors = G.neighbors(node)
    for i in range(0, len(neighbors)):
        n1 = neighbors[i]
        for n2 in neighbors[i + 1:]:
            edge = find_correct_edge(n1, n2, ntype)
            if edge is not None:
                edge['weight'] += G[node][n1]['weight']
            else:
                new.add_edge(n1, n2, weight=G[node][n1]['weight'], type=ntype)


# Return true if a hyperlink edge exists between the nodes and false otherwise
def hyperlink_exists(node, neighbor):
    try:
        edges = new[node][neighbor]
    except KeyError:
        return False

    for edge in edges:
        if edges[edge]['type'] == 'hyperlink':
            return True
    return False


def copy_hyperlinks(node):
    for neighbor in G[node]:
        if types[neighbor] == 'site' and not hyperlink_exists(node, neighbor):
            new.add_edge(node, neighbor, weight=G[node][neighbor]['weight'], type='hyperlink')


# Select only the nodes with degree below threshold
def degree_subgraph(G, threshold):
    # Calculate degree distribution
    degrees = G.degree()
    # values = np.fromiter(iter(degrees.values()), dtype=np.int)
    # average = np.average(values)

    nodes = []
    for node in degrees:
        if types[node] == 'site' or degrees[node] < threshold:
            nodes.append(node)

    subgraph = G.subgraph(nodes)
    return subgraph


if __name__ == '__main__':
    print("Reading graph file")
    [G, types] = pickle.load(open('undirectional_total.graph', 'rb'))

    G = degree_subgraph(G, 500)
    new = nx.MultiGraph()

    for i, node in enumerate(G):
        if i % 10000 == 0:
            print("Processed {} nodes".format(i))
        try:
            ntype = types[node]
        except KeyError:
            ntype = 'site'

        # Connect all domain neighbours
        if ntype == 'script' or ntype == 'cookie':
            connect_neighbours(node, ntype)
        else:
            copy_hyperlinks(node)

    print("Writing graph to file")
    pickle.dump(new, open('induced.graph', 'wb'))
