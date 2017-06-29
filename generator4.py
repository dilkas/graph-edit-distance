import random
import sys
import common

# Generates two graphs for a subgraph isomorphism problem with given numbers of vertices, edge probabilities,
# and a probability for each vertex to be labelled. Labels are randomly chosen from 1 to vertices1+vertices2.
# Generates two files:
# 1. Two graphs for a maximum common induced subgraph problem
# 2. The same problem encoded as a max clique problem
if len(sys.argv) < 7:
    print ('Usage: python {} vertices1 edge_probability1 label_probability_1 vertices2 edge_probability2 label_probability_2'.format(sys.argv[0]))
    exit()

parameters = []
for i in range(3, len(sys.argv), 3):
    parameters.append((int(sys.argv[i - 2]), float(sys.argv[i - 1]), float(sys.argv[i])))
n1 = parameters[0][0]
n2 = parameters[1][0]

matrices = []
for n, _, _ in parameters:
    matrix = []
    for i in range(n):
        matrix.append([0] * n)
    matrices.append(matrix)
labels = []
for i, (n, p, l) in enumerate(parameters):
    local_labels = []
    for j in range(n):
        local_labels.append(random.randint(1, n1 + n2) if random.random() < l else 0)
        for k in range(j):
            if random.random() < p:
                matrices[i][j][k] = matrices[i][k][j] = 1
    labels.append(local_labels)

with open('mcis.dzn', 'w') as f:
    for i in range(len(parameters)):
        f.write('n{} = {};\n'.format(i + 1, parameters[i][0]))
        f.write(common.adjacency_matrix(matrices[i], 'adjacent' + str(i + 1)))
        f.write('vLabel{} = [{}];\n'.format(i + 1, ', '.join(map(str, labels[i]))))

encoding = {}
n = 0
for v1 in range(n1):
    for v2 in range(n2):
        if labels[0][v1] == labels[1][v2]:
            encoding[(v1, v2)] = n
            n += 1
if n == 0:
    exit(1)

clique = []
for i in range(n):
    clique.append([0] * n)

for a, b in encoding:
    for c, d in encoding:
        if a != c and b != d and matrices[0][a][c] == matrices[1][b][d]:
            clique[encoding[(a, b)]][encoding[(c, d)]] = 1

with open('mc.dzn', 'w') as f:
    f.write('n = {};\n'.format(n))
    f.write(common.adjacency_matrix(clique))
