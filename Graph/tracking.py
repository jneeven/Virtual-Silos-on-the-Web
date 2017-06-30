"""
Using the MongoDB data, create the tracking graph as described in the thesis.
Is saved as a GML file so it can be easily read and visualised.
"""

import networkx as nx
from pymongo import MongoClient
from multiprocessing import Pool
import time
import matplotlib.pyplot as plt
import numpy as np

# Create all outbound edges for this domain and count
# individual tracking code domains
def create_edges(domain, cookies, scripts):
    for source in cookies:
        g.add_node(source, type='cookie')
        g.add_edge(domain, source, weight=cookies[source])

    for source in scripts:
        g.add_node(source, type='script')
        g.add_edge(domain, source, weight=scripts[source])


# Return all outbound edges and their strengths, leaving out hyperlinks
def process_domain(domain):
    cookies = {}
    for cookie in domain['cookies']:
        if cookie == '':
            print("empty domain")
            continue
        try:
            cookies[cookie] += 1
        except KeyError:
            cookies[cookie] = 1

    scripts = {}
    for script in domain['scripts']:
        if script == '':
            print("empty domain")
            continue
        try:
            scripts[script] += 1
        except KeyError:
            scripts[script] = 1

    return domain['_id'], cookies, scripts


if __name__ == '__main__':
    client = MongoClient('localhost', 27017, connect=False)
    db = client['second']
    domains = db.domains

    g = nx.DiGraph()
    pool = Pool(processes=3)
    total_start = time.time()

    # Get edges for each domain
    print("Collecting all nodes and edges")
    results = []
    for obj in domains.find({}):
        results.append(pool.apply_async(process_domain, (obj, )))
    print("Done, took {} seconds".format(time.time() - total_start))

    start = time.time()
    # Construct graph from result
    print("Constructing graph from data")
    for res in results:
        domain, cookies, scripts = res.get()
        create_edges(domain, cookies, scripts)
    print("Done, took {} seconds".format(time.time() - start))

    #top_50_sources()

    start = time.time()
    print("Writing output file")
    # Other output formats are available (i.e. pickle)
    nx.write_gml(g, 'tracking_graph.gml')
    print("Done, took {} seconds".format(time.time() - start))


    print("Total elapsed time: {} seconds".format(time.time() - total_start))
