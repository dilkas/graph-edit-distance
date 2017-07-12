import itertools
import math
import os
import sys
from xml.etree import ElementTree
from munkres import Munkres
import common

# takes two GLX files and produces a DZN file for the GED models: the vertex-weight-only variant
if len(sys.argv) < 3:
    print('Usage: python {} first_file.glx second_file.glx [int]'.format(sys.argv[0]))
    exit()

x = [[], []]
y = [[], []]
vertex_type = [[], []]

adjacent = [[], []]
edge_types = [[], []]
edge_counts = [0, 0]
for i, data_file in enumerate([sys.argv[1], sys.argv[2]]):
    for element in ElementTree.parse(data_file).getroot()[0]:
        if element.tag == 'node':
            x[i].append(float(element[0][0].text))
            y[i].append(float(element[1][0].text))
            vertex_type[i].append(element[2][0].text)
        else:
            edge_counts[i] += 1
            if adjacent[i] == []: # once we know its size
                for _ in range(len(x[i])):
                    adjacent[i].append([0] * len(x[i]))
                    edge_types[i].append([[] for _ in range(len(x[i]))])
            f, t = [int(j) for j in element.attrib.values()]
            adjacent[i][f][t] = adjacent[i][t][f] = 1
            edge_types[i][f][t] = edge_types[i][t][f] = [child[0].text for child in element if child.attrib['name'].startswith('type')]

with open(common.new_filename(sys.argv[1:3], 'clique2'), 'w') as f:
    # output vertex and edge counts
    for i in range(len(adjacent)):
        f.write('v{} = {};\n'.format(i + 1, len(adjacent[i])))
        f.write('e{} = {};\n'.format(i + 1, edge_counts[i]))

    # collecting data to be used later
    substitutions = []
    for i, row1 in enumerate(edge_types[0]):
        three_d = []
        for j, types1 in enumerate(row1):
            two_d = []
            for k, row2 in enumerate(edge_types[1]):
                two_d.append([0 if len(types1) == 0 and len(types2) == 0 else -common.edge_substitution_cost(types1, types2)
                              for l, types2 in enumerate(row2)])
            three_d.append(two_d)
        substitutions.append(three_d)

    weights = [-45] * len(adjacent[1]) # vertex insertion
    for i, t1 in enumerate(vertex_type[0]):
        weights.append(-45) # vertex deletion
        for j, t2 in enumerate(vertex_type[1]): # vertex substitution
            weights.append(-0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2) if t1 == t2 else -90)

    # edge insertion
    for i in range(len(adjacent[1])):
        for j in range(i):
            if adjacent[1][i][j]:
                weights.append(-7.5 * len(edge_types[1][i][j]))
        
    for i1 in range(len(adjacent[0])):
        for i2 in range(i1):
            if not adjacent[0][i1][i2]:
                continue
            weights.append(-7.5 * len(edge_types[0][i1][i2])) # edge deletion
            for j1 in range(len(adjacent[1])):
                for j2 in range(j1):
                    if adjacent[1][j1][j2]: # edge substitution
                        weights.append(substitutions[i1][i2][j1][j2])

    if len(sys.argv) > 3:
        weights = map(int, weights)
    f.write(common.vector(weights, 'weights'))

    vertices = list(common.vertices2(len(adjacent[0]), len(adjacent[1]), adjacent))
    adjacency_matrix = []
    for _ in range(len(vertices)):
        adjacency_matrix.append([1] * len(vertices))
    for i, op1 in enumerate(vertices):
        for j, op2 in enumerate(vertices):
            if op1[0] == 'v' and op2[0] == 'v':
                if op1[1] == op2[1] != None or op1[2] == op2[2] != None:
                    adjacency_matrix[i][j] = 0
            elif op1[0] == 'e' and op2[0] == 'e':
                if op1[1:3] == op2[1:3] and None not in op1[1:3] or op1[3:] == op2[3:] and None not in op1[3:]:
                    adjacency_matrix[i][j] = 0
            elif op1[0] == 'v' and None not in op2:
                if (op1[1] is None and op1[2] in op2[3:] or op1[2] is None and op1[1] in op2[1:3] or
                    None not in op1 and (op1[1] in op2[1:3] and op1[2] not in op2[3:] or op1[2] in op2[3:] and op1[1] not in op2[1:3])):
                    adjacency_matrix[i][j] = adjacency_matrix[j][i] = 0
    f.write(common.matrix(adjacency_matrix, 'adjacent'))