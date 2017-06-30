"""
For all detected communities, create a subgraph and calculate some metrics. Finally,
display the distributions of these metrics over all communities.
"""

import networkx as nx
import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np


# Plot degree and size distributions
def distribution(G):
    # Calculate degree distribution
    degree = G.degree()
    # Sort by value (is low to high)
    sorted_degrees = sorted(degree.items(), key=lambda x: x[1])
    degrees = np.array(sorted_degrees)[:, 1].astype(np.float)
    print("Average degree:\n{}"
          .format(np.average(degrees)))

    dfig = plt.subplot(121)
    # left, right = np.percentile(degrees, [0, 99])
    left, right = (0, np.log10(np.max(degrees)))
    h = plt.hist(degrees, bins=np.logspace(left, right, 50),
                 facecolor='green', alpha=0.75, log=True)
    dfig.set_xscale("log")
    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    plt.suptitle('Community size and degree distributions')
    plt.grid(True)

    # Calculate size distribution
    sizes = []
    for node in G.nodes_iter(data=True):
        sizes.append(node[1]['domaincount'])
    sizes = np.array(sizes)
    print("Average size:\n{}"
          .format(np.average(sizes)))

    sfig = plt.subplot(122, sharey=dfig)
    # left, right = np.percentile(sizes, [0, 99])
    left, right = (0, np.log10(np.max(sizes)))
    n, bins, patches = plt.hist(sizes, bins=np.logspace(left, right, 50), cumulative=False,
                                facecolor='blue', alpha=0.75, log=True)
    plt.setp(plt.xticks()[1])  # , rotation=30, rotation_mode="anchor", ha="right")
    sfig.set_xscale("log")
    plt.xlabel('Size')
    plt.grid(True)

    plt.show()


# Select only the nodes with degree below threshold
def degree_subgraph(G, threshold):
    # Calculate degree distribution
    degrees = G.degree()
    # values = np.fromiter(iter(degrees.values()), dtype=np.int)
    # average = np.average(values)

    nodes = []
    for node in degrees:
        if degrees[node] < threshold:
            nodes.append(node)

    subgraph = G.subgraph(nodes)
    return subgraph


# Select only nodes with size above threshold
def size_subgraph(G, size):
    nodes = []
    for node in G.nodes_iter(data=True):
        if node[1]['domaincount'] >= size:
            nodes.append(node[0])

    subgraph = G.subgraph(nodes)
    return subgraph


# Select only nodes with above average density and at least size 4.
def density_subgraph(G, metrics):
    average = np.average(metrics[:, 1])
    nodes = []
    for node_info in metrics:
        if node_info[1] > average and node_info[2] >= 4:
            nodes.append(node_info[0])

    subgraph = G.subgraph(nodes)
    for node_info in metrics:
        try:
            subgraph.node[node_info[0]]['density'] = node_info[1]
        except KeyError:
            pass
    return subgraph


def calculate_metrics(G):
    # Only works for undirected
    # clustering = nx.average_clustering(G)

    density = nx.density(G)

    size = G.number_of_nodes()

    avg_conn = nx.average_node_connectivity(G)

    degrees = np.fromiter(iter(G.degree().values()), dtype=np.int)
    avg_degree = np.average(degrees)

    # giant_comp_size = len(max(nx.strongly_connected_components(G), key=len))
    # strongly_connected_ratio = giant_comp_size/size

    # Only works when connected
    # diameter = nx.diameter(G)

    # betweenness centrality?

    return [density, size, avg_degree, avg_conn]  # strongly_connected_ratio]


def multiplot(data, index, xlabel):
    fig = plt.subplot(220 + index)

    # If no values bigger than zero, don't plot.
    maxv = np.max(data)
    if maxv == 0:
        return

    left = 0
    right = np.log10(np.max(data))
    if right < 1:
        left = -2
    bins = np.logspace(left, right, 50)

    n, bins, patches = plt.hist(data, bins=bins, facecolor='green', log=True, alpha=0.75)
    plt.xlabel(xlabel)
    fig.set_xscale("log")
    if index % 2 != 0:
        plt.ylabel('Frequency')
    plt.grid(True)
    return fig


def metrics_distribution(metrics):
    avg_density = np.average(metrics[:, 1])
    avg_size = np.average(metrics[:, 2])
    avg_degree = np.average(metrics[:, 3])
    avg_conn = np.average(metrics[:, 4])
    # avg_strong_conn = np.average(metrics[:, 5])

    for i, conn in enumerate(metrics[:, 4]):
        if conn < 1:
            print(metrics[i])

    # counter = 0
    # for strc in metrics[:, 5]:
    #     if strc == 1:
    #         counter += 1
    # print("Strongly connected: {}".format(counter))

    print("Average density: {}\nAverage size: {}\nAverage degree: {}\n"
          "Average connectivity: {}\n"
          .format(avg_density, avg_size, avg_degree, avg_conn))

    multiplot(metrics[:, 1], 1, 'Density')
    multiplot(metrics[:, 2], 2, 'Size')
    multiplot(metrics[:, 3], 3, 'Average degree')
    multiplot(metrics[:, 4], 4, 'Average connectivity')
    # multiplot(metrics[:, 5], 4, 'Strongly connected ratio')
    plt.suptitle('Metrics of community sub-graphs')
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    # plt.savefig('distribution.png', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    # print("Loading community graph")
    # G = nx.read_gml('output/total_community_graph.gml')
    # # # distribution(G)
    # #
    # filtered = degree_subgraph(G, 17.95)
    # # # filtered = size_subgraph(filtered, 20)
    # # # nx.write_gml(filtered, 'filtered.gml')
    # #
    # print("Loading original graph")
    # # original = nx.read_gml('output/induced_graph.gml')
    # original = pickle.load(open('induced.graph', 'rb'))
    # #
    # metrics = []
    # print("Calculating subgraph metrics")
    # for node, data in filtered.nodes_iter(data=True):
    #     nodes = data['domains']
    #     if type(nodes) != list:
    #         nodes = [nodes]
    #     # try:
    #     #     nodes += data['scripts']
    #     # except KeyError:
    #     #     pass
    #     # try:
    #     #     nodes += data['cookies']
    #     # except KeyError:
    #     #     pass
    #     sub = original.subgraph(nodes)
    #     metrics.append([node] + calculate_metrics(sub))
    
    # pickle.dump(metrics, open('total_com_metrics', 'wb'))
    metrics = pickle.load(open('tracking_com_metrics', 'rb'))
    metrics = np.array(metrics)
    metrics_distribution(metrics)

    # nx.write_gml(filtered, 'subgraph.gml')