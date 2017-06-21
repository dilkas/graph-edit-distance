import sys
import common

# converts DIMACS graph files into MiniZinc *.dzn format
output_filename = sys.argv[1][:sys.argv[1].rfind('.')] + '.dzn'
with open(sys.argv[1]) as in_file, open(output_filename, 'w') as out_file:
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
    out_file.write(common.adjacency_matrix(matrix))
