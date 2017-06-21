import random
import sys
import common

# generates graphs for the MiniZinc models, size_of_clique is used for the decision problem
if len(sys.argv) < 3:
    print ('Usage: python {} number_of_vertices edge_probability [size_of_clique]'.format(sys.argv[0]))
    exit()

n = int(sys.argv[1])
p = float(sys.argv[2])

matrix = []
for i in range(n):
    matrix.append(['0'] * n)

for i in range(n):
    for j in range(i):
        if random.random() < p:
            matrix[i][j] = matrix[j][i] = '1'

with open('generated.dzn', 'w') as f:
    f.write('n = {};\n'.format(n))
    if len(sys.argv) >= 4:
        f.write('k = {};\n'.format(sys.argv[3]))
    f.write(common.adjacency_matrix(matrix))
