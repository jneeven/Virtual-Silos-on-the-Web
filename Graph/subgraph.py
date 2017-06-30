"""
Given the original graph, the community graph and a set of node IDs, create a subgraph
of a specific community as a separate file, which can then be visualised.
"""

import networkx as nx
import pickle

if __name__ == '__main__':
    print("Reading in graph files.")
    # original = pickle.load(open('induced.graph', 'rb'))
    original = nx.read_gml('subgraph36.gml')
    community = nx.read_gml('36_communities.gml')

    labels = [7]
    for label in labels:
        print("Creating subgraph")
        node = community.node[label]
        nodes = node['domains']
        if type(nodes) != list:
            nodes = [nodes]
        try:
            nodes += node['scripts']
        except KeyError:
            pass
        try:
            nodes += node['cookies']
        except KeyError:
            pass
        subgraph = original.subgraph(nodes)
        nx.write_gml(subgraph, 'subgraph'+ str(label) + '.gml')
