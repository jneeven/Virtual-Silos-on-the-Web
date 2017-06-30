"""
Load undirected graph and perform community detection by 
Louvain Modularity Optimisation. Community results are output as a new graph file,
in which each node is a community.
"""

import community
import networkx as nx
import time
import sys
import pickle


# For the given node, add the domain to the correct list and increase
# the correct counter
def update_list(C, index, list_name, counter_name, domain):
    try:
        C.node[index][list_name].append(domain)
        C.node[index][counter_name] += 1
    except KeyError:
        C.node[index][list_name] = [domain]
        C.node[index][counter_name] = 1


# Store list of sites, cookies and scripts in each community node
def add_labels(C, partitions, types):
    for domain in partitions:
        type = types[domain]
        if type == 'cookie':
            update_list(C, partitions[domain], 'cookies', 'cookiecount', domain)
        elif type == 'script':
            update_list(C, partitions[domain], 'scripts', 'scriptcount', domain)
        else:
            update_list(C, partitions[domain], 'domains', 'domaincount', domain)


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

    print("Reading in graph file.")
    [G, types] = pickle.load(open('undirection_total.graph', 'rb'))
    print("Done, took {} seconds.".format(time.time() - total_start))

    start = time.time()
    print("Running Louvain algorithm")
    partitions = community.best_partition(G, resolution=1)
    NX = community.induced_graph(partitions, G)
    add_labels(NX, partitions, types)
    print("Done, took {} seconds.".format(time.time() - start))

    print("Modularity:")
    print(community.modularity(partitions, G))

    start = time.time()
    print("Writing community graph to file")
    NX.remove_edges_from(NX.selfloop_edges())
    nx.write_gml(NX, 'community_louvain.gml')
    print("Done, took {} seconds.".format(time.time() - start))

    print("Total elapsed time: {} seconds.".format(time.time() - total_start))
    print("Nodes: {}".format(nx.number_of_nodes(NX)))
