import itertools
import os
import re
import sys
from xml.etree import ElementTree
from common import matrix, four_dimensions

# converts CMU GLX files from the GD4GED database to MiniZinc *.dzn format
for pairs_of_files in itertools.combinations(os.listdir(sys.argv[1]), 2):
    x = [[], []]
    y = [[], []]
    adjacent = [[], []]
    dist = [[], []]
    for i, data_file in enumerate(pairs_of_files):
        for element in ElementTree.parse(os.path.join(sys.argv[1], data_file)).getroot()[0]:
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

    with open(os.path.join('graphs', 'cmu', '-'.join([re.search('[0-9]+', s).group(0) for s in pairs_of_files]) + '.dzn'), 'w') as f:
        for i in range(len(adjacent)):
            f.write('n{} = {};\n'.format(i + 1, len(adjacent[i])))
            f.write(matrix(adjacent[i], 'adjacent{}'.format(i + 1)))
        f.write('vertexDeletionCost = [{}];\n'.format(', '.join([str(sys.maxsize)] * len(adjacent[0]))))
        f.write('vertexInsertionCost = [{}];\n'.format(', '.join([str(sys.maxsize)] * len(adjacent[1]))))
        f.write(matrix([[0] * len(adjacent[1])] * len(adjacent[0]), 'vertexSubstitutionCost'))
        deletions = []
        for distance in dist[0]:
            deletions.append([0.5 * d for d in distance])
        f.write(matrix(deletions, 'edgeDeletionCost'))
        insertions = []
        for distance in dist[1]:
            insertions.append([0.5 * d for d in distance])
        f.write(matrix(insertions, 'edgeInsertionCost'))
        substitutions = []
        for row1 in dist[0]:
            for dist1 in row1:
                for row2 in dist[1]:
                    for dist2 in row2:
                        substitutions.append(0.5 * abs(dist1 - dist2))
        f.write(four_dimensions(substitutions, 'edgeSubstitutionCost'))
