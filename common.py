import os
from munkres import Munkres

def matrix(matrix, name='adjacent'):
    return name + ' = [' + '\n'.join('| ' + ', '.join(str(c) for c in row) for row in matrix) + ' |];\n'

def four_dimensions(a, name):
    '''Transforms a flat list into a MiniZinc 4-dimensional array.'''
    return '{} = array4d(1..n1, 1..n1, 1..n2, 1..n2, [{}]);\n'.format(name, ', '.join(map(str, a)))

def vector(a, name):
    return '{} = [{}];\n'.format(name, ', '.join(map(str, a)))

def new_filename(files, d='ged'):
    return os.path.join('graphs', d, '-'.join([os.path.basename(f[:f.find('.')]) for f in files]) + '.dzn')

def dimacs_filename(files, db):
    return os.path.join('graphs', 'dimacs', db, '-'.join([os.path.basename(f[:f.rfind('.')]) for f in files]) + '.txt')

def full_path(filename, db='grec'):
    return os.path.join('graphs', 'db', db.upper()+'-GED', db.upper(), filename)

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

def mwc_adjacency_matrix(adjacent):
    '''Takes a list of two adjacency matrices and returns an adjacency matrix for the min weight clique problem'''
    vertices = list(vertices2(len(adjacent[0]), len(adjacent[1]), adjacent))
    adjacency_matrix = []
    for _ in range(len(vertices)):
        adjacency_matrix.append([1] * len(vertices))
    for i, op1 in enumerate(vertices):
        for j, op2 in enumerate(vertices):
            if op1[0] == 'v' and op2[0] == 'v':
                if op1[1] == op2[1] != None or op1[2] == op2[2] != None:
                    adjacency_matrix[i][j] = 0
            elif op1[0] == 'e' and op2[0] == 'e':
                if op1[1:3] == op2[1:3] and None not in op1[1:3] or op1[3:] == op2[3:] and None not in op1[3:]:
                    adjacency_matrix[i][j] = 0
            elif op1[0] == 'v' and None not in op2:
                if (op1[1] is None and op1[2] in op2[3:] or op1[2] is None and op1[1] in op2[1:3] or
                    None not in op1 and (op1[1] in op2[1:3] and op1[2] not in op2[3:] or op1[2] in op2[3:] and op1[1] not in op2[1:3])):
                    adjacency_matrix[i][j] = adjacency_matrix[j][i] = 0
    return adjacency_matrix

def output_dimacs(filenames, directory, adjacent, adjacency_matrix, edge_counts, weights):
    with open(dimacs_filename(filenames, directory), 'w') as f:
        v1 = len(adjacent[0])
        v2 = len(adjacent[1])
        e0 = (v1 + 1) * (v2 + 1) - 1
        f.write('p edge {} {} {} {} {} {}\n'.format(len(adjacency_matrix), sum(adjacency_matrix[i][j] for i in range(len(adjacency_matrix))
                                                                               for j in range(i)), v1, v2, edge_counts[0], edge_counts[1]))

        for i in range(len(adjacency_matrix)):
            for j in range(i):
                if adjacency_matrix[i][j]:
                    f.write('e {} {}\n'.format(i + 1, j + 1))

        for i, w in enumerate(weights):
            f.write('n {} {}\n'.format(i + 1, w))

        # s marks the independent sets that we must choose a vertex from
        for i in range(v1):
            f.write('s {}\n'.format(' '.join([str((i + 1) * (v2 + 1) + j) for j in range(v2 + 1)])))
        for j in range(v2):
            f.write('s {}\n'.format(' '.join([str(i * (v2 + 1) + j + 1) for i in range(v1 + 1)])))
        for i in range(edge_counts[0]):
            f.write('s {}\n'.format(' '.join([str(e0 + (i + 1) * (edge_counts[1] + 1) + j) for j in range(edge_counts[1] + 1)])))
        for j in range(edge_counts[1]):
            f.write('s {}\n'.format(' '.join([str(e0 + i * (edge_counts[1] + 1) + j + 1) for i in range(edge_counts[0] + 1)])))
