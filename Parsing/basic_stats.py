"""
Query the data from the MongoDB and perform calculate some statistics such as the
distribution of the amount of hyperlinks per domain, the most used scripts, etc.
"""


from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import pickle


hyperlink_counts = []
script_counts = []
cookie_counts = []

cookies = {}
scripts = {}


# Create figure of top 50 cookie or script sources
def create_overview(type, data):
    title = 'Top 50 {} sources'.format(type)

    fig = plt.figure()

    h = plt.bar(np.arange(0, data.shape[0]), np.flipud(data[:, 1]).astype(np.int))
    xticks_pos = [0.65 * patch.get_width() + patch.get_xy()[0] for patch in h]
    plt.xticks(xticks_pos, np.flipud(data[:, 0]), ha='right', size=8, rotation=45)
    plt.ylabel('Frequency')
    plt.yscale('log')

    plt.title(title)
    fig.subplots_adjust(bottom=0.5)
    plt.show()
    plt.close(fig)


def top_50_sources():
    # script top 50
    name = 'apis.google.com/_/scs/apps-static/_/js/k=oz.gapi.nl.43JAI8YPjas.O/m=plusone/rt=j/sv=1/d=1/ed=1/am=AQ/rs=AGLTcCOl4ILqyPOrt75ObgDfKa3vVKWH-w/cb=gapi.loaded_0'
    scripts['apis.google.com/_/scs/apps-static/_/js/k=oz.gapi.nl.43JAI8YPjas.O/m=plusone/'] = scripts[name]
    del scripts[name]
    sorted_scripts = sorted(scripts.items(), key=lambda x: x[1])[-50:]
    create_overview('script', np.array(sorted_scripts))

    # cookie top 50
    sorted_cookies = sorted(cookies.items(), key=lambda x: x[1])[-50:]
    create_overview('cookie', np.array(sorted_cookies))


def multiplot(data, index, xlabel):
    fig = plt.subplot(130 + index)

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
    if index == 1:
        plt.ylabel('Frequency')
    plt.grid(True)
    return fig


# Return all outbound edges and their strengths
def process_domain(domain):
    hyperlink_counts.append(len(domain['hyperlinks']))
    script_counts.append(len(np.unique(domain['scripts'])))
    cookie_counts.append(len(np.unique(domain['cookies'])))

    for source in domain['cookies']:
        try:
            cookies[source] += 1
        except KeyError:
            cookies[source] = 1

    for source in domain['scripts']:
        try:
            scripts[source] += 1
        except KeyError:
            scripts[source] = 1


def parse_db():
    client = MongoClient('localhost', 27017, connect=False)
    db = client['second']
    domains = db.domains

    for obj in domains.find({}):
        process_domain(obj)


if __name__ == '__main__':
    parse_db()

    # pickle.dump([hyperlink_counts, script_counts, cookie_counts, cookies, scripts],
    #             open('basic_stats', 'wb'))

    # [hyperlink_counts, script_counts, cookie_counts, cookies, scripts] = pickle.load(
    #     open('basic_stats', 'rb'))

    top_50_sources()
    exit(0)
    multiplot(hyperlink_counts, 1, 'Outgoing hyperlinks')
    multiplot(script_counts, 2, 'Scripts')
    multiplot(cookie_counts, 3, 'Cookies')
    plt.suptitle('Distribution of amount of hyperlinks, scripts and cookies on each domain')
    plt.show()
