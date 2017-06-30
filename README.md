# Virtual Silos on the web
This repo hosts the files used in the thesis project as carried out 
by Jelmer Neeven at the University of Amsterdam. Although the thesis
project has been concluded, the research is by far not finished.
I welcome anyone to read the thesis, make improvements to the code, 
and continue the research. I acknowledge the fact that the code is
very much in a suboptimal state and does not always follow good practice,
for which I apologize. The short amount of time that was allowed for the
project to be carried out meant I had to prioritise research over maintainability,
and this code was in no way intended to be released as a product to the public. I cannot
guarantee that all the scripts are working as supposed.

### Repo structure
Reddit URLs are collected by Reddit Urls/url-collector/main.py,
the post and comment thresholds are determined in histogram.py, and finally
the URLs are filtered using filter_urls.py.

The resulting list of seed URLs is used by Crawler/recursiveMaster.js, 
which is executed by the following command:
```
phantomjs recursiveMaster.js outputDirectory
```
Specific settings such as the maximum runtime and backup frequency
are specified in the source code.

The resulting files should be merged with Parsing/merge_files.py,
and the resulting data file should be imported into MongoDB using
import_db.py.

Finally, the actual graph creation and analysis happens in the Graph/
folder. Using hyperlinks.py, total_graph.py and tracking.py, the respective
graphs are created. These GML files are to be converted to undirectional graphs
using convert_to_undirectional.py before Louvain Modularity Optimisation
can be run on them using louvain.py.
When the communities have been obtained, there are several files
to compute different metrics in different ways. Subgraphs can be created
using the specific community node ID and the file subgraph.py,
after which they can be visualised in Gephi for the analysis.


Should anyone be interested, my daily work and decisions are logged in
productivity_log.md. Note that it was never meant to be public, so there may be
details that do not make sense to anyone but myself. Still, it should provide
insight in reasons behind some of the aspects of the crawler, data import etc.
