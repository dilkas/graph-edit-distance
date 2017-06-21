def adjacency_matrix(matrix):
    '''formats a graph adjacency matrix for MiniZinc'''
    return 'adjacent = [' + '\n'.join('| ' + ', '.join(row) for row in matrix) + ' |];\n'
