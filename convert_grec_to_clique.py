import itertools
import math
import os
import sys
from xml.etree import ElementTree
from munkres import Munkres
import common

def sign(number):
    return 1 if number >= 0 else -1

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

def vertices(V1, V2):
    '''Given the number of vertices in both graphs, generates a sequence of vertices for the clique problem'''
    for v2 in range(V2):
        yield ('insertion', v2)
    for v1 in range(V1):
        yield ('deletion', v1)
        for v2 in range(V2):
            yield ('substitution', v1, v2)

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
        f.write('v{} = {};\n'.format(i + 1, len(adjacent[i])))
        f.write(common.matrix(adjacent[i], 'adjacent{}'.format(i + 1)))

    vertex_weights = [45] * len(adjacent[1]) # insertion costs
    for i, t1 in enumerate(vertex_type[0]):
        vertex_weights.append(45) # deletion cost
        for j, t2 in enumerate(vertex_type[1]):
            vertex_weights.append(min(0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2), 90) if t1 == t2 else 90)
    f.write(common.vector(vertex_weights, 'vertexWeights'))

    # TODO: complete and check this mess
    edge_weights = []
    for op1 in vertices(len(adjacent[0]), len(adjacent[1])):
        row = []
        for op2 in vertices(len(adjacent[0]), len(adjacent[1])):
            if op1[0] == 'insertion':
                if op2 == op1 or op2[0] == 'deletion' or op2[0] == 'substitution' and op2[2] == op1[1]:
                    row.append(0)
                elif op2[0] != 'deletion':
                    row.append(INSERTION_COST if adjacent[1][op1[2]][op2[2]] else 0)
                else:
                    raise RuntimeError('This should never happen')
            if op1[0] == 'deletion':
                if op2[0] == 'insertion' or op2 == op1 or op2[0] == 'substitution' and op2[1] == op1[1]:
                    row.append(0)
                elif op2[0] != 'insertion':
                    row.append(DELETION_COST if adjacent[0][op1[1]][op2[1]] else 0)
                else:
                    raise RuntimeError('This should never happen')
            else:
                if (op2[0] == 'substitution' and (op2[1] == op1[1] or op2[2] == op1[1]) or
                    op2[0] == 'insertion' and op2[1] == op1[2] or op2[0] == 'deletion' and op2[1] == op1[1]):
                    row.append(0)
                elif op2[0] == 'substitution':
                    row.append(min(SUBSTITUTION_COST, DELETION_COST + INSERTION_COST))
                else:
                    row.append(INSERTION_COST if op2[0] == 'insertion' else DELETION_COST)
        edge_weights.append(row)

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
