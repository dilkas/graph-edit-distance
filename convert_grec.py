import itertools
import math
import os
import re
import sys
from xml.etree import ElementTree
import common

def sign(number):
    return 1 if number >= 0 else -1

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
    f.write(common.vector([45] * len(adjacent[0]), 'vertexDeletionCost'))
    f.write(common.vector([45] * len(adjacent[1]), 'vertexInsertionCost'))
    substitutions = []
    for i, t1 in enumerate(vertex_type[0]):
        row = []
        for j, t2 in enumerate(vertex_type[1]):
            row.append(min(0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2), 90) if t1 == t2 else 90)
        substitutions.append(row)
    f.write(common.matrix(substitutions, 'vertexSubstitutionCost'))
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
                    if i == k and j == l:
                        print(types1, types2)
                    substitutions.append(sum([7.5 for t1 in types1 for t2 in types2 if t1 != t2]))
    f.write(common.four_dimensions(substitutions, 'edgeSubstitutionCost'))
