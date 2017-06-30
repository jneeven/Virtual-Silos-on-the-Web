"""
Calculates some statistics of a given graph. Not actually used in the thesis.
"""

import networkx as nx
import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np


def create_histogram(data, title):
    fig = plt.figure()

    left = np.min(data)
    right = np.max(data)

    n, bins, patches = plt.hist(data, bins=np.linspace(left, right, 50), cumulative=False, weights=np.zeros_like(data) + 1. / len(data), facecolor='green', alpha=0.75)

    plt.xlim(xmax=right)
    plt.xlabel('Degree')
    plt.ylabel('Relative frequency')
    plt.title(title)
    plt.grid(True)
    return fig


def degree_distribution(G):
    degree = G.degree()
    # Sort by value (is low to high)
    sorted_degrees = sorted(degree.items(), key=lambda x: x[1])
    values = np.array(sorted_degrees)[:, 1].astype(np.float)
    fig = create_histogram(values, 'Degree distribution')
    print("Top 10 domains by degree:\n{}".format(sorted_degrees[-10:]))
    print("Average degree:\n{}"
          .format(np.average(values)))
    plt.show()
    plt.close(fig)


# Takes a long time
def betweenness_distribution(G):
    betweenness = nx.betweenness_centrality(G)
    # Sort by value (is low to high)
    sorted_btw = sorted(betweenness.items(), key=lambda x: x[1])

    values = np.array(sorted_btw)[:, 1].astype(np.float)
    fig = create_histogram(values, 'Betweenness distribution')
    print("Top 10 domains by betweenness:\n{}".format(sorted_btw[-10:]))
    print("Average betweenness:\n{}"
          .format(np.average(values)))
    plt.show()
    plt.close(fig)


def create_overview(data):
    title = 'Top 50 PageRank domains'.format(type)

    fig = plt.figure()

    h = plt.bar(np.arange(0, data.shape[0]), np.flipud(data[:, 1]).astype(np.float))
    xticks_pos = [0.65 * patch.get_width() + patch.get_xy()[0] for patch in h]
    plt.xticks(xticks_pos, np.flipud(data[:, 0]), ha='right', size=8, rotation=45)
    plt.ylabel('Score')

    plt.title(title)
    fig.subplots_adjust(bottom=0.5)
    plt.show()
    plt.close(fig)


def default_metrics(G):
    print("Nodes: {}\nEdges: {}\n".format(nx.number_of_nodes(G),
                                          nx.number_of_edges(G)))

    print("Calculating degree distribution.")
    degree_distribution(G)

    # print("Calculating betweenness distribution")
    # betweenness_distribution(G)

    print("Calculating density.")
    print(nx.density(G))

    # print("Average clustering coefficient:")
    # print(nx.average_clustering(G))

    # print("PageRank:")
    # pagerank = nx.pagerank(G)
    # create_overview(np.array(sorted(pagerank.items(), key=lambda x: x[1])[-50:]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file specified")
        exit(0)

    print("Reading graph file")
    try:
        [G, _] = pickle.load(open(sys.argv[1], 'rb'))
    except ValueError:
        G = nx.read_gml(sys.argv[1])

    default_metrics(G)

    print("Calculating largest connected component")
    # Gc = max(nx.connected_component_subgraphs(G), key=len)
    Gc = max(nx.weakly_connected_component_subgraphs(G), key=len)
    print("Stats for largest component:")
    default_metrics(Gc)

    # Doesn't work if the graphs are not connected.
    print("Calculating average shortest path length.")
    print(nx.average_shortest_path_length(Gc))

    # Doesn't work if the graphs are not connected.
    print("Calculating diameter.")
    print(nx.diameter(Gc))
