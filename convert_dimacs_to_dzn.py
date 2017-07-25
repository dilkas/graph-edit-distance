import sys
import common

# converts DIMACS graph files into MiniZinc *.dzn format

if len(sys.argv) < 2:
    print('Usage: python {} DIMACS_file'.format(sys.argv[0]))
    exit()

with open(sys.argv[1]) as in_file, open(sys.argv[1][:sys.argv[1].rfind('.')] + '.dzn', 'w') as out_file:
    for line in in_file:
        if line[0] == 'p':
            n = int(line.split()[2])
            matrix = [] # initialize the matrix
            for i in range(n):
                matrix.append(['0'] * n)
            out_file.write('n = {};\n'.format(n))
        elif line[0] == 'e':
            v1, v2 = [int(v) - 1 for v in line.split()[1:]]
            matrix[v1][v2] = matrix[v2][v1] = '1'
    out_file.write(common.matrix(matrix))
