def adjacency_matrix(matrix):
    '''formats a graph adjacency matrix for MiniZinc'''
    return 'adjacent = [' + '\n'.join('| ' + ', '.join(str(c) for c in row) for row in matrix) + ' |];\n'
