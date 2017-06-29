import random
import sys
import common

# generates two graphs for a subgraph isomorphism problem with given numbers of vertices and edge probabilities
# Generates two files:
# 1. Two graphs for a maximum common induced subgraph problem
# 2. The same problem encoded as a max clique problem
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

with open('mcis.dzn', 'w') as f:
    for i in range(len(parameters)):
        f.write('n{} = {};\n'.format(i + 1, parameters[i][0]))
        f.write(common.adjacency_matrix(matrices[i], 'adjacent' + str(i + 1)))

n1 = parameters[0][0]
n2 = parameters[1][0]
n = n1 * n2
clique = []
for i in range(n):
    clique.append([0] * n)

for v2 in range(n2):
    for u2 in range(n2):
        if u2 == v2:
            continue
        for v1 in range(n1):
            for u1 in range(n1):
                if u1 == v1:
                    continue
                if matrices[0][v1][u1] == matrices[1][v2][u2]:
                    clique[v1 * n2 + v2][u1 * n2 + u2] = 1

with open('mc.dzn', 'w') as f:
    f.write('n = {};\n'.format(parameters[0][0] * parameters[1][0]))
    f.write(common.adjacency_matrix(clique))
