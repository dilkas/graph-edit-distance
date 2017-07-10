import itertools
import math
import os
import sys
from xml.etree import ElementTree
from munkres import Munkres
import common

def edge_substitution_cost(types1, types2):
    start_freq = len(types1)
    end_freq = len(types2)
    n = start_freq + end_freq
    matrix = []
    for _ in range(n):
        matrix.append([0] * n)
    for i in range(start_freq):
        for j in range(end_freq):
            matrix[i][j] = 0 if types1[i] == types2[j] else 30
        for j in range(end_freq, n):
            matrix[i][j] = 15 if j - end_freq == i else float('inf')
    for i in range(start_freq, n):
        for j in range(end_freq):
            matrix[i][j] = 15 if i - start_freq == j else float('inf')
    return 0.5 * sum([matrix[i][j] for i, j in Munkres().compute(matrix)])

# takes two GLX files and produces a DZN file for the GED models
if len(sys.argv) < 3:
    print('Usage: python {} first_file.glx second_file.glx'.format(sys.argv[0]))
    exit()

x = [[], []]
y = [[], []]
vertex_type = [[], []]

adjacent = [[], []]
edge_types = [[], []]
for i, data_file in enumerate([sys.argv[1], sys.argv[2]]):
    for element in ElementTree.parse(data_file).getroot()[0]:
        if element.tag == 'node':
            x[i].append(float(element[0][0].text))
            y[i].append(float(element[1][0].text))
            vertex_type[i].append(element[2][0].text)
        else:
            if adjacent[i] == []: # once we know its size
                for _ in range(len(x[i])):
                    adjacent[i].append([0] * len(x[i]))
                    vector = []
                    for _ in range(len(x[i])):
                        vector.append([])
                    edge_types[i].append(vector)
            f, t = [int(j) for j in element.attrib.values()]
            adjacent[i][f][t] = adjacent[i][t][f] = 1
            edge_types[i][f][t] = edge_types[i][t][f] = [child[0].text for child in element if child.attrib['name'].startswith('type')]

with open(common.new_filename(sys.argv[1:]), 'w') as f:
    for i in range(len(adjacent)):
        f.write('n{} = {};\n'.format(i + 1, len(adjacent[i])))
        f.write(common.matrix(adjacent[i], 'adjacent{}'.format(i + 1)))
    f.write(common.vector([45] * len(adjacent[1]), 'vertexInsertionCost'))
    substitutions = []
    for i, t1 in enumerate(vertex_type[0]):
        substitutions.append(45) # vertex deletion cost
        for j, t2 in enumerate(vertex_type[1]):
            substitutions.append(0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2) if t1 == t2 else 90)
    f.write(common.two_dimensions(substitutions, 'vertexSubstitutionCost'))
    edge_ops = [[], []]
    names = ['edgeDeletionCost', 'edgeInsertionCost']
    for i in range(len(adjacent)):
        for j in range(len(adjacent[i])):
            edge_ops[i].append([7.5 * len(edge_types[i][j][k]) for k in range(len(adjacent[i]))])
        f.write(common.matrix(edge_ops[i], names[i]))
    substitutions = []
    for i, row1 in enumerate(edge_types[0]):
        for j, types1 in enumerate(row1):
            for k, row2 in enumerate(edge_types[1]):
                for l, types2 in enumerate(row2):
                    substitutions.append(0 if len(types1) == 0 and len(types2) == 0 else edge_substitution_cost(types1, types2))
    f.write(common.four_dimensions(substitutions, 'edgeSubstitutionCost'))
