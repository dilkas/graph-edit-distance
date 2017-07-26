def vector(a, name):
    return '{} = [{}];\n'.format(name, ', '.join(map(str, a)))

def matrix(matrix, name='adjacent'):
    return name + ' = [' + '\n'.join('| ' + ', '.join(str(c) for c in row) for row in matrix) + ' |];\n'

def two_dimensions(a, name):
    return '{} = array2d(1..n1, 0..n2, [{}]);\n'.format(name, ', '.join(map(str, a)))

def four_dimensions(a, name):
    '''Transforms a flat list into a MiniZinc 4-dimensional array.'''
    return '{} = array4d(1..n1, 1..n1, 1..n2, 1..n2, [{}]);\n'.format(name, ', '.join(map(str, a)))
