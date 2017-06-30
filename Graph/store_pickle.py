"""
Read GML graph and save as pickle data. Loading a pickled graph is much faster than GML.
"""

import sys
import pickle
import time
import networkx as nx

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Specify an input and output file.")
        exit(0)
    total_start = time.time()

    print("Reading in graph file.")
    G = nx.read_gml(sys.argv[1])
    print("Done, took {} seconds.".format(time.time() - total_start))

    print("Writing output file")
    pickle.dump(G, open(sys.argv[2], 'wb'))
