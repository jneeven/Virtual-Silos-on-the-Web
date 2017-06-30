"""
An attempt to detect communities using k-clique percolation. Does not seem to yield any results
after running for a long time.
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
    if len(sys.argv) < 3:
        print("No input or output file specified")
        exit(0)
    total_start = time.time()

    print("Reading in graph file.")
    [G, types] = pickle.load(open(sys.argv[1], 'rb'))
    print("Done, took {} seconds.".format(time.time() - total_start))

    print("Finding cliques")
    cliques = nx.find_cliques(G)

    print("Finding communities")
    for com in nx.k_clique_communities(G, 10, cliques):
        print("Community: ", com)
