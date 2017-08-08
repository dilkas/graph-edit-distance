import sys
import common
import dzn_formatting

# Converts DIMACS graph files into DZN format
if len(sys.argv) < 2:
    print('Usage: python {} DIMACS_file'.format(sys.argv[0]))
    exit()

with open(sys.argv[1]) as in_file, open(sys.argv[1][:sys.argv[1].rfind('.')] + '.dzn', 'w') as out_file:
    for line in in_file:
        if line[0] == 'p':
            n = int(line.split()[2])
            matrix = common.initialize_matrix(n)
            out_file.write('n = {};\n'.format(n))
        elif line[0] == 'e':
            v1, v2 = [int(v) - 1 for v in line.split()[1:]]
            matrix[v1][v2] = matrix[v2][v1] = 1
    out_file.write(dzn_formatting.matrix(matrix))
