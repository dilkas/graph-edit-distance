import itertools
import random
import sys
import common
import dzn_formatting

SUBGRAPH_FILENAME = 'subgraph.dzn'
CLIQUE_FILENAME = 'clique.dzn'


class CliqueGenerator(common.Script):
    '''Generates graphs for max clique optimization & decision problems.'''

    parameters = [common.Parameter('number_of_vertices'), common.Parameter('edge_probability', float), common.Parameter('size_of_clique', int, False)]

    def __init__(self):
        super().__init__()
        unsorted_matrix = common.initialize_matrix(self.arguments['number_of_vertices'])

        # fill the matrix
        for i in range(self.arguments['number_of_vertices']):
            for j in range(i):
                if random.random() < self.arguments['edge_probability']:
                    unsorted_matrix[i][j] = unsorted_matrix[j][i] = 1

        # sort the matrix
        indices = sorted(range(self.arguments['number_of_vertices']), key=lambda x: sum(unsorted_matrix[x]), reverse=True)
        matrix = common.initialize_matrix(self.arguments['number_of_vertices'])
        for i, old_i in enumerate(indices):
            for j, old_j in enumerate(indices):
                matrix[i][j] = unsorted_matrix[old_i][old_j]

        # output the matrix
        with open(CLIQUE_FILENAME, 'w') as f:
            f.write('n = {};\n'.format(self.arguments['number_of_vertices']))
            if 'size_of_clique' in self.arguments:
                f.write('k = {};\n'.format(self.arguments['size_of_clique']))
            f.write(dzn_formatting.matrix(matrix))


class SubgraphGenerator(common.Script):
    '''Generates 2 graphs for subgraph isomorphism or maximum common induced subgraph problem.'''
    parameters = [common.Parameter('number_of_vertices1'), common.Parameter('edge_probability1'),
                  common.Parameter('number_of_vertices2'), common.Parameter('edge_probability2')]

    def __init__(self):
        # Instance variables are initialized so that subclasses could use them
        self.first_command_line_argument = 2
        self.check_command_line_arguments()
        self.arguments = [(int(sys.argv[i - 1]), float(sys.argv[i])) for i in range(3, len(sys.argv), 2)]
        self.generate_and_write_to_file()

    def generate_and_write_to_file(self):
        self.matrices = [common.initialize_matrix(self.arguments[i][0]) for i in range(len(self.arguments))]

        for i in range(len(self.arguments)):
            for j in range(self.arguments[i][0]):
                for k in range(j):
                    if random.random() < self.arguments[i][1]:
                        self.matrices[i][j][k] = self.matrices[i][k][j] = 1

        with open(SUBGRAPH_FILENAME, 'w') as f:
            for i in range(len(self.arguments)):
                f.write('n{} = {};\n'.format(i + 1, self.arguments[i][0]))
                f.write(dzn_formatting.matrix(self.matrices[i], 'adjacent' + str(i + 1)))


class SubgraphCliqueEncoding(SubgraphGenerator):
    '''Uses SubgraphGenerator to generate a maximum common induced subgraph problem and then encodes it as max clique.'''

    def __init__(self):
        super().__init__()

        n1 = self.arguments[0][0]
        n2 = self.arguments[1][0]
        clique = common.initialize_matrix(n1 * n2)
        for v2, u2 in itertools.product(range(n2), repeat=2):
            if u2 == v2:
                continue
            for v1, u1 in itertools.product(range(n1), repeat=2):
                if u1 != v1 and self.matrices[0][v1][u1] == self.matrices[1][v2][u2]:
                    clique[v1 * n2 + v2][u1 * n2 + u2] = 1

        with open(CLIQUE_FILENAME, 'w') as f:
            f.write('n = {};\n'.format(n1 * n2))
            f.write(dzn_formatting.matrix(clique))


class LabelledSubgraphCliqueEncoding(SubgraphGenerator):
    '''Uses SubgraphGenerator to generate 2 labelled graphs for a maximum common induced subgraph problem and then
    encodes them as max clique. Label_probability is the probability of assigning a random label in
    [1, vertices1 + vertices2]. Otherwise a 0 is assigned.'''
    parameters = list(itertools.chain.from_iterable((common.Parameter('vertices' + str(i)), common.Parameter('edge_probability' + str(i)),
                                                     common.Parameter('label_probability' + str(i))) for i in range(1, 3)))

    def __init__(self):
        # parse the command line arguments
        self.first_command_line_argument = 2
        self.check_command_line_arguments()
        self.arguments = [(int(sys.argv[i - 2]), float(sys.argv[i - 1]), float(sys.argv[i])) for i in range(4, len(sys.argv), 3)]

        # call the superclass to generate the 2 graphs
        self.generate_and_write_to_file()
        n1 = self.arguments[0][0]
        n2 = self.arguments[1][0]

        # generate the labels
        labels = [] # labels[i] is a list of labels for all vertices of graph i
        for n, _, l in self.arguments:
            labels.append([random.randint(1, n1 + n2) if random.random() < l else 0 for j in range(n)])

        # write then to the file already generated by SubgraphGenerator
        with open(SUBGRAPH_FILENAME, 'a') as f:
            for i in range(len(self.arguments)):
                f.write('vLabel{} = [{}];\n'.format(i + 1, ', '.join(map(str, labels[i]))))

        # assign a new 'name' for all pairs of vertices that can be matched
        encoding = {}
        n = 0
        for v1 in range(n1):
            for v2 in range(n2):
                if labels[0][v1] == labels[1][v2]:
                    encoding[(v1, v2)] = n
                    n += 1

        # generate an adjacency matrix for the clique problem
        clique = common.initialize_matrix(n)
        for (a, b), (c, d) in itertools.product(encoding, repeat=2):
            if a != c and b != d and self.matrices[0][a][c] == self.matrices[1][b][d]:
                clique[encoding[(a, b)]][encoding[(c, d)]] = 1

        # write it to file
        with open(CLIQUE_FILENAME, 'w') as f:
            f.write('n = {};\n'.format(n))
            f.write(dzn_formatting.matrix(clique))


if __name__ == '__main__':
    generators = {'clique': CliqueGenerator, 'subgraph': SubgraphGenerator, 'subgraphClique': SubgraphCliqueEncoding,
                  'labelledSubgraph': LabelledSubgraphCliqueEncoding}
    if len(sys.argv) < 2 or sys.argv[1] not in generators:
        print('Choose one of the generators ({}) and run'.format(', '.join(generators)))
        print('    python {} generator'.format(sys.argv[0]))
        print('for more information.')
    else:
        generators[sys.argv[1]]()
