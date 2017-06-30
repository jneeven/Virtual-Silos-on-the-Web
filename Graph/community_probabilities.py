"""
For all communities in a graph, calculate the amount of nodes that are in the same community
and also share a piece of tracking code.
"""

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


# Return true if a tracking edge exists between the nodes and false otherwise
def tracking_exists(node, neighbor):
    try:
        edges = G[node][neighbor]
    except KeyError:
        return False

    for edge in edges:
        if edges[edge]['type'] == 'cookie' or edges[edge]['type'] == 'script':
            return True
    return False


if __name__ == '__main__':
    print("Reading graph file")
    induced = pickle.load(open('induced.graph', 'rb'))

    print("Loading community graph")
    comm = nx.read_gml('output/hyperlink_community_graph.gml')

    tracking_percentages = []
    counter = 0

    # Create a subgraph for every community
    for node, data in comm.nodes_iter(data=True):
        counter += 1
        if counter % 50 == 0:
            print("Processed {} communities".format(counter))
        nodes = data['domains']
        G = induced.subgraph(nodes)
        amt_nodes = float(G.number_of_nodes())
        comm_percentage = 0.0
        # For all nodes in community, count the percentage of nodes that share at least one piece of
        # tracking code
        for i, node in enumerate(G):
            tracking = 0
            for neighbor in G[node]:
                edges = G[node][neighbor]
                if tracking_exists(node, neighbor):
                    tracking += 1
            comm_percentage += tracking/amt_nodes
        try:
            tracking_percentages.append(comm_percentage/amt_nodes)
        except ZeroDivisionError:
            print("subgraph size zero.")

    pickle.dump(tracking_percentages, open('tracking_percentages', 'wb'))
    # tracking_percentages = pickle.load(open('tracking_percentages', 'rb'))

    fig = plt.subplot(111)

    data = np.array(tracking_percentages)
    left = np.min(data)
    right = np.max(data)
    n, bins, patches = plt.hist(data, log=True, bins=np.linspace(left, right, 50), facecolor='green', alpha=0.75)

    plt.xlim(xmax=right)
    plt.xlabel('Percentage of nodes in the same community that is tracking-connected')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
