import itertools
import os
import re
import sys
from xml.etree import ElementTree
import common

# converts CMU GLX files from the GDR4GED database to DIMACS
x = [[], []]
y = [[], []]
adjacent = [[], []]
dist = [[], []]
edge_counts = [0, 0]
for i, data_file in enumerate(sys.argv[1:3]):
    for element in ElementTree.parse(data_file).getroot()[0]:
        if element.tag == 'node':
            x[i].append(float(element[0][0].text))
            y[i].append(float(element[1][0].text))
        else:
            if adjacent[i] == []: # once we know its size
                for _ in range(len(x[i])):
                    adjacent[i].append([0] * len(x[i]))
                    dist[i].append([0] * len(x[i]))
            f, t = [int(j) - 1 for j in element.attrib.values()]
            adjacent[i][f][t] = adjacent[i][t][f] = 1
            dist[i][f][t] = dist[i][t][f] = float(element[0][0].text)
            edge_counts[i] += 1

weights = [sys.maxsize] * len(adjacent[1]) # vertex insertion
for _ in range(len(adjacent[0])): # vertex deletion & substitution
    weights += [sys.maxsize] + [0] * len(adjacent[1])
weights += [0.5 * dist[1][i][j] for i in range(len(dist[1])) for j in range(i) if adjacent[1][i][j]] # edge insertion
for i1 in range(len(adjacent[0])):
    for i2 in range(i1):
        if not adjacent[0][i1][i2]:
            continue
        weights.append(0.5 * dist[0][i1][i2]) # edge deletion
        for j1 in range(len(adjacent[1])):
            for j2 in range(j1):
                if adjacent[1][j1][j2]:
                    weights.append(0.5 * abs(dist[0][i1][i2] - dist[1][j1][j2]))

common.output_dimacs(sys.argv[1:3], 'cmu', adjacent, common.mwc_adjacency_matrix(adjacent), edge_counts, weights)
