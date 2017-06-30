"""
Convert directed graph to undirected graph, and save as a pickle file for quick loading.
"""

import community
import networkx as nx
import time
import sys
import pickle


# Add up weights in both directions and combine to a single edge
# Output the new, undirectional single graph.
# Found on http://stackoverflow.com/questions/15590812/networkx-convert-multigraph-into-simple-graph-with-weighted-edges
def convert_to_simple(M):
    symmetry_count = 0
    G = nx.Graph()
    for u, v, data in M.edges_iter(data=True):
        w = data['weight']
        if G.has_edge(u, v):
            symmetry_count += 2
            G[u][v]['weight'] += w
        else:
            G.add_edge(u, v, weight=w)
    print("Symmetric edges: {}".format(symmetry_count))
    return G


# For every node, get its type and store in global type dict
def get_types(G):
    types = {}
    for node in G:
        try:
            types[node] = G.node[node]['type']
        except KeyError:
            types[node] = 'site'
    return types


if __name__ == '__main__':
    #if len(sys.argv) < 3:
    #    print("No input or output file specified")
    #    exit(0)
    total_start = time.time()

    print("Reading in graph file.") # specify the graph file to use here
    G = nx.read_gml('total_graph.gml')
    print("Done, took {} seconds.".format(time.time() - total_start))

    start = time.time()
    print("Converting to undirectional graph.")
    types = get_types(G)
    G = convert_to_simple(G)
    print("Done, took {} seconds.".format(time.time() - start))

    start = time.time()
    print("Writing undirectional graph to file")
    pickle.dump([G, types], open('undirection_total.graph', 'wb')) # specify output file here
    print("Done, took {} seconds.".format(time.time() - start))

    print("Total elapsed time: {} seconds.".format(time.time() - total_start))
