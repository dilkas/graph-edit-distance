import random
import sys
import common
from collections import namedtuple


class Generator(Object):

    Argument = namedtuple('Argument', ['name', 'mandatory'])
    Argument.__new__.__defaults__ = ('', True)

    def initialize_matrix(n):
        matrix = []
        for _ in range(n):
            matrix.append([0] * n)
        return matrix

    def run():
        if len(sys.argv) < len(filter(lambda a: a.mandatory, self.arguments)) + 1:
            print('Usage: python', sys.argv[0], ' '.join(a.name if a.mandatory else '[' + a.name + ']' for a in self.arguments))
            exit()
        

class CliqueGenerator(Generator):
    '''Generates graphs for max clique optimization & decision problems.'''

    arguments = [Argument('number_of_vertices'), Argument('edge_probability'), Argument('size_of_clique', False)]

    def run():
        super()

        n = int(sys.argv[1])
        p = float(sys.argv[2])
        unsorted_matrix = initialize_matrix(n)

        # fill the matrix
        for i in range(n):
            for j in range(i):
                if random.random() < p:
                    unsorted_matrix[i][j] = unsorted_matrix[j][i] = 1

        # sort the matrix
        indices = sorted(range(n), key=lambda x: sum(unsorted_matrix[x]), reverse=True)
        matrix = initialize_matrix(n)
        for i, old_i in enumerate(indices):
            for j, old_j in enumerate(indices):
                matrix[i][j] = unsorted_matrix[old_i][old_j]

        # output the matrix
        with open('generated.dzn', 'w') as f:
            f.write('n = {};\n'.format(n))
            if len(sys.argv) >= 4:
                f.write('k = {};\n'.format(sys.argv[3]))
            f.write(common.adjacency_matrix(matrix))


class SubgraphGenerator(Generator):
    '''Generates 2 graphs for subgraph isomorphism problem.'''
    arguments = [Argument('pattern_number_of_vertices'), Argument('pattern_edge_probability'),
                 Argument('target_number_of_vertices'), Argument('target_edge_probability')]

    def run():
        super()

        parameters = []
        for i in range(2, len(sys.argv), 2):
            parameters.append((int(sys.argv[i - 1]), float(sys.argv[i])))
        matrices = [initialize_matrix(n) for n, _ in parameters]

        for i, (n, p) in enumerate(parameters):
            for j in range(n):
                for k in range(j):
                    if random.random() < p:
                        matrices[i][j][k] = matrices[i][k][j] = 1

        with open('generated.dzn', 'w') as f:
            for i in range(len(parameters)):
                f.write('n{} = {};\n'.format(i + 1, parameters[i][0]))
                f.write(common.adjacency_matrix(matrices[i], 'adjacent' + str(i + 1)))
