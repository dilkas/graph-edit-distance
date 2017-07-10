import itertools
import math
import os
import sys
from xml.etree import ElementTree
from munkres import Munkres
import common

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
                    edge_types[i].append([[] for _ in range(len(x[i]))])
            f, t = [int(j) for j in element.attrib.values()]
            adjacent[i][f][t] = adjacent[i][t][f] = 1
            edge_types[i][f][t] = edge_types[i][t][f] = [child[0].text for child in element if child.attrib['name'].startswith('type')]

with open(common.new_filename(sys.argv[1:], 'clique1'), 'w') as f:
    for i in range(len(adjacent)):
        f.write('v{} = {};\n'.format(i + 1, len(adjacent[i])))

    vertex_weights = [-45] * len(adjacent[1]) # insertion costs
    for i, t1 in enumerate(vertex_type[0]):
        vertex_weights.append(-45) # deletion cost
        for j, t2 in enumerate(vertex_type[1]):
            vertex_weights.append(-0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2) if t1 == t2 else -90)
    f.write(common.vector(vertex_weights, 'vertexWeights'))

    # collecting data to be used later
    edge_ops = [[], []] # deletions and insertions
    for i in range(len(adjacent)):
        for j in range(len(adjacent[i])):
            edge_ops[i].append([-7.5 * len(edge_types[i][j][k]) for k in range(len(adjacent[i]))])
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

    edge_weights = []
    for op1 in common.vertices(len(adjacent[0]), len(adjacent[1])):
        row = []
        for op2 in common.vertices(len(adjacent[0]), len(adjacent[1])):
            if op1[0] == 'insertion':
                if op2 == op1 or op2[0] == 'deletion' or op2[0] == 'substitution' and op2[2] == op1[2]:
                    row.append(0)
                elif op2[0] != 'deletion':
                    row.append(edge_ops[1][op1[2]][op2[2]] if adjacent[1][op1[2]][op2[2]] else 0)
                else:
                    raise RuntimeError('This should never happen')
            elif op1[0] == 'deletion':
                if op2[0] == 'insertion' or op2 == op1 or op2[0] == 'substitution' and op2[1] == op1[1]:
                    row.append(0)
                elif op2[0] != 'insertion':
                    row.append(edge_ops[0][op1[1]][op2[1]] if adjacent[0][op1[1]][op2[1]] else 0)
                else:
                    raise RuntimeError('This should never happen')
            else:
                if (op2[0] == 'substitution' and (op2[1] == op1[1] or op2[2] == op1[2]) or
                    op2[0] == 'insertion' and op2[2] == op1[2] or op2[0] == 'deletion' and op2[1] == op1[1]):
                    row.append(0)
                elif op2[0] == 'substitution':
                    if not adjacent[0][op1[1]][op2[1]] and adjacent[1][op1[2]][op2[2]]:
                        row.append(edge_ops[1][op1[2]][op2[2]]) # insert an edge
                    elif adjacent[0][op1[1]][op2[1]] and not adjacent[1][op1[2]][op2[2]]:
                        row.append(edge_ops[0][op1[1]][op2[1]]) # delete an edge
                    else:
                        row.append(max(substitutions[op1[1]][op2[1]][op1[2]][op2[2]], edge_ops[0][op1[1]][op2[1]] + edge_ops[1][op1[2]][op2[2]]))
                else:
                    row.append(edge_ops[1][op1[2]][op2[2]] if op2[0] == 'insertion' else edge_ops[0][op1[1]][op2[1]])
        edge_weights.append(row)
    f.write(common.matrix(edge_weights, 'edgeWeights'))

    adjacency_matrix = []
    for op1 in common.vertices(len(adjacent[0]), len(adjacent[1])):
        row = []
        for op2 in common.vertices(len(adjacent[0]), len(adjacent[1])):
            row.append(0 if op1[1] == op2[1] != None or op1[2] == op2[2] != None else 1)
        adjacency_matrix.append(row)
    f.write(common.matrix(adjacency_matrix, 'adjacent'))
    # sanity check for 5,5-vertex case: all pairs should be adjacent
    #for i in [6, 13, 20, 27, 34]:
    #    for j in [6, 13, 20, 27, 34]:
    #        if i != j:
    #            print(i, j, adjacency_matrix[i][j])
