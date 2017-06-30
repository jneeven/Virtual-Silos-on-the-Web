"""
Takes all the files output by the crawler and merges them to one large file.
File name should be specified in the code below.
"""

import fileinput


if __name__ == '__main__':
    outputfile = open('merged_output', 'w')
    for i in range(1, 120):
        filename = '/home/jelmer/Cluster/1494079284/output' + str(i)
        # Loads lines lazily so we don't have everything in memory
        for line in fileinput.input(filename):
            outputfile.write(line)
    outputfile.close()
