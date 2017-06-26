import random
import sys
import common

# generates two graphs for a subgraph isomorphism problem with given numbers of vertices and edge probabilities
if len(sys.argv) < 5:
    print ('Usage: python {} number_of_vertices1 edge_probability1 number_of_vertices2 edge_probability2'.format(sys.argv[0]))
    exit()

parameters = []
for i in range(2, len(sys.argv), 2):
    parameters.append((int(sys.argv[i - 1]), float(sys.argv[i])))

matrices = []
for n, _ in parameters:
    matrix = []
    for i in range(n):
        matrix.append([0] * n)
    matrices.append(matrix)

for i, (n, p) in enumerate(parameters):
    for j in range(n):
        for k in range(j):
            if random.random() < p:
                matrices[i][j][k] = matrices[i][k][j] = 1

with open('generated.dzn', 'w') as f:
    for i in range(len(parameters)):
        f.write('n{} = {};\n'.format(i + 1, parameters[i][0]))
        f.write(common.adjacency_matrix(matrices[i], 'adjacent' + str(i + 1)))
