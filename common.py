import os
from munkres import Munkres

def matrix(matrix, name='adjacent'):
    return name + ' = [' + '\n'.join('| ' + ', '.join(str(c) for c in row) for row in matrix) + ' |];\n'

def four_dimensions(a, name):
    '''Transforms a flat list into a MiniZinc 4-dimensional array.'''
    return '{} = array4d(1..n1, 1..n1, 1..n2, 1..n2, [{}]);\n'.format(name, ', '.join(map(str, a)))

def vector(a, name):
    return '{} = [{}];\n'.format(name, ', '.join(map(str, a)))

def new_filename(files, d = 'ged'):
    return os.path.join('graphs', d, '-'.join([os.path.basename(f[:f.find('.')]) for f in files]) + '.dzn')

def full_path(filename):
    return os.path.join('graphs', 'db', 'GREC-GED', 'GREC', filename)

def two_dimensions(a, name):
    return '{} = array2d(1..n1, 0..n2, [{}]);\n'.format(name, ', '.join(map(str, a)))

def edge_substitution_cost(types1, types2):
    start_freq = len(types1)
    end_freq = len(types2)
    n = start_freq + end_freq
    matrix = []
    for _ in range(n):
        matrix.append([0] * n)
    for i in range(start_freq):
        for j in range(end_freq):
            matrix[i][j] = 0 if types1[i] == types2[j] else 30
        for j in range(end_freq, n):
            matrix[i][j] = 15 if j - end_freq == i else float('inf')
    for i in range(start_freq, n):
        for j in range(end_freq):
            matrix[i][j] = 15 if i - start_freq == j else float('inf')
    return 0.5 * sum([matrix[i][j] for i, j in Munkres().compute(matrix)])

def vertices(V1, V2):
    '''Given the number of vertices in both graphs, generates a sequence of vertices for the clique problem'''
    for v2 in range(V2):
        yield ('insertion', None, v2)
    for v1 in range(V1):
        yield ('deletion', v1, None)
        for v2 in range(V2):
            yield ('substitution', v1, v2)

def vertices2(V1, V2, adjacency_matrices):
    '''Includes edge operations among vertices. V1 and V2 are numbers,
    adjacency_matrices is a list of two adjacency matrix (for source and target graphs)'''
    # vertices
    for v2 in range(V2):
        yield ('v', None, v2) # insertions
    for v1 in range(V1):
        yield ('v', v1, None) # deletions
        for v2 in range(V2):
            yield ('v', v1, v2) # substitutions
    
    # edges
    for j1 in range(len(adjacency_matrices[1])):
        for j2 in range(j1):
            if adjacency_matrices[1][j1][j2]:
                yield ('e', None, None, j1, j2) # insertions
    for i1 in range(len(adjacency_matrices[0])):
        for i2 in range(i1):
            if not adjacency_matrices[0][i1][i2]:
                continue
            yield ('e', i1, i2, None, None) # deletions
            for j1 in range(len(adjacency_matrices[1])):
                for j2 in range(j1):
                    if adjacency_matrices[1][j1][j2]:
                        yield ('e', i1, i2, j1, j2) # substitutions
