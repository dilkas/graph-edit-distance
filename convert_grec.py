import itertools
import math
import os
import re
import sys
from xml.etree import ElementTree
from common import matrix, four_dimensions, vector

# converts GREC GLX files from the GD4GED database to MiniZinc *.dzn format
for pairs_of_files in itertools.combinations(filter(lambda x: x.endswith('gxl') and x.startswith('image3'), os.listdir(sys.argv[1])), 2):
    x = [[], []]
    y = [[], []]
    typ = [[], []]
    adjacent = [[], []]
    type0 = [[], []]
    for i, data_file in enumerate(pairs_of_files):
        for element in ElementTree.parse(os.path.join(sys.argv[1], data_file)).getroot()[0]:
            if element.tag == 'node':
                x[i].append(float(element[0][0].text))
                y[i].append(float(element[1][0].text))
                typ[i].append(element[2][0].text)
            else:
                if adjacent[i] == []: # once we know its size
                    for _ in range(len(x[i])):
                        adjacent[i].append([0] * len(x[i]))
                        type0[i].append([0] * len(x[i]))
                f, t = [int(j) for j in element.attrib.values()]
                adjacent[i][f][t] = adjacent[i][t][f] = 1
                type0[i][f][t] = type0[i][t][f] = element[1][0].text

    with open(os.path.join('graphs', 'grec', '-'.join([re.search('[0-9]+_[0-9]+', s).group(0) for s in pairs_of_files]) + '.dzn'), 'w') as f:
        for i in range(len(adjacent)):
            f.write('n{} = {};\n'.format(i + 1, len(adjacent[i])))
            f.write(matrix(adjacent[i], 'adjacent{}'.format(i + 1)))
        f.write(vector([45] * len(adjacent[0]), 'vertexDeletionCost'))
        f.write(vector([45] * len(adjacent[1]), 'vertexInsertionCost'))
        substitutions = []
        for i, t1 in enumerate(typ[0]):
            row = []
            for j, t2 in enumerate(typ[1]):
                row.append(0.5 * math.sqrt((x[0][i] - x[1][j])**2 + (y[0][i] - y[1][j])**2) if t1 == t2 else 90)
            substitutions.append(row)
        f.write(matrix(substitutions, 'vertexSubstitutionCost'))
        f.write(matrix([[7.5] * len(adjacent[0])] * len(adjacent[0]), 'edgeDeletionCost'))
        f.write(matrix([[7.5] * len(adjacent[1])] * len(adjacent[1]), 'edgeInsertionCost'))
        substitutions = []
        for row1 in type0[0]:
            for t1 in row1:
                for row2 in type0[1]:
                    for t2 in row2:
                        substitutions.append(0 if t1 == t2 else 30)
        f.write(four_dimensions(substitutions, 'edgeSubstitutionCost'))
