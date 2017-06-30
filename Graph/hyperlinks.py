"""
Using the MongoDB data, create the hyperlink graph as described in the thesis.
Is saved as a GML file so it can be easily read and visualised.
"""

import networkx as nx
from pymongo import MongoClient
from multiprocessing import Pool
import time


# Create all outbound edges for this domain
def create_edges(domain, edges):
    for edomain in edges:
        g.add_edge(domain, edomain, weight=edges[edomain])


# Return all outbound edges and their strengths
def process_domain(domain):
    connections = {}
    for link in domain['hyperlinks']:
        link_domain = link['domain']
        if link_domain == '':
            print("empty domain")
            continue
        try:
            connections[link_domain] += 1
        except KeyError:
            connections[link_domain] = 1

    return domain['_id'], connections


if __name__ == '__main__':
    client = MongoClient('localhost', 27017, connect=False)
    db = client['second']
    domains = db.domains

    g = nx.DiGraph()
    pool = Pool(processes=3)

    start = time.time()

    # Get edges for each domain
    print("Getting all nodes and edges")
    results = []
    for obj in domains.find({}):
        results.append(pool.apply_async(process_domain, (obj, )))

    # Construct graph from result
    print("Constructing graph from data")
    for res in results:
        domain, edges = res.get()
        create_edges(domain, edges)

    # Other output formats are available (i.e. pickle)
    print("Writing graph to file")
    nx.write_gml(g, 'hyperlink_graph.gml')

    print("Program finished. Elapsed time: {}".format(time.time() - start))
