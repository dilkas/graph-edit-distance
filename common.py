def adjacency_matrix(matrix, name='adjacent'):
    '''formats a graph adjacency matrix for MiniZinc'''
    return name + ' = [' + '\n'.join('| ' + ', '.join(str(c) for c in row) for row in matrix) + ' |];\n'
