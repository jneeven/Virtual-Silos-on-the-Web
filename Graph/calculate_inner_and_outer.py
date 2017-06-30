"""
For a given community, calculate the amount of hyperlinks that go to other domains
within the community (inner) and the amount of hyperlinks that go to domains outside
of this community (outer).
"""

import networkx as nx
import pickle

if __name__ == '__main__':
    print("Reading in graph files.")
    hyperlinks = nx.read_gml('output/hyperlink_graph.gml')
    # The graph that contains the specific community
    community = nx.read_gml('36_communities.gml')

    print("Creating subgraph")
    node = community.node[7] # In this case, we are only interested in subcommunity 7
    nodes = node['domains']
    if type(nodes) != list:
        nodes = [nodes] # The list of domains in subcommunity 7

    inner = 0
    outer = 0
    for node in nodes:
        try:
            edges = hyperlinks[node]
            for edge in edges:
                if edge in nodes:
                    # inner += edges[edge]['weight']
                    inner += 1
                else:
                    # outer += edges[edge]['weight']
                    outer += 1
        except KeyError:
            pass

    print("Inner edges:", inner)
    print("Outer edges:", outer)
