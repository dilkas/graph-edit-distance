import random
import sys
import common

# generates graphs for the MiniZinc models, size_of_clique is used for the decision problem
if len(sys.argv) < 3:
    print ('Usage: python {} number_of_vertices edge_probability [size_of_clique]'.format(sys.argv[0]))
    exit()

n = int(sys.argv[1])
p = float(sys.argv[2])

# initialize the matrix
unsorted_matrix = []
for i in range(n):
    unsorted_matrix.append([0] * n)

# fill the matrix
for i in range(n):
    for j in range(i):
        if random.random() < p:
            unsorted_matrix[i][j] = unsorted_matrix[j][i] = 1

#print(unsorted_matrix)

# sort the matrix
indices = sorted(range(n), key=lambda x: sum(unsorted_matrix[x]), reverse=True)
matrix = []
for i in range(n):
    matrix.append([0] * n)
for i, old_i in enumerate(indices):
    for j, old_j in enumerate(indices):
        matrix[i][j] = unsorted_matrix[old_i][old_j]

# output the matrix
with open('generated.dzn', 'w') as f:
    f.write('n = {};\n'.format(n))
    if len(sys.argv) >= 4:
        f.write('k = {};\n'.format(sys.argv[3]))
    f.write(common.adjacency_matrix(matrix))
