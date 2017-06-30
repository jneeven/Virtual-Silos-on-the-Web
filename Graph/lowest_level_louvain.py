"""
Run Louvain Modularity, but return just the first iteration of the results, meaning
the biggest amount of clusters (and consequently, the smallest clusters).
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
def add_labels(C, partitions):
    for domain in partitions:
        update_list(C, partitions[domain], 'domains', 'domaincount', domain)


if __name__ == '__main__':
    print("Reading in graph file.")
    [G, types] = pickle.load(open('output/undirectional_hyperlink.graph', 'rb'))

    dendrogram = community.generate_dendrogram(G)
    partitions = community.partition_at_level(dendrogram, 0)
    print(community.modularity(partitions, G))
    NX = community.induced_graph(partitions, G)
    add_labels(NX, partitions)

    NX.remove_edges_from(NX.selfloop_edges())
    nx.write_gml(NX, 'smallest_communities.gml')
