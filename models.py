class VertexWeights:
    '''Takes two graphs and encodes a graph edit distance problem between them as a clique with weights on vertices only.'''

    def __init__(self, g1, g2, output_format, filename):
        self.g1 = g1
        self.g2 = g2
        self.n1 = g1.number_of_vertices
        self.n2 = g2.number_of_vertices
        self.vertices = list(self.generate_vertices())
        self.N = len(vertices)
        adjacency_matrix = self.construct_adjacency_matrix()
        weights = self.generate_weights()
        if output_format == 'dzn':
            write_dzn(filename)
        elif output_format == 'dimacs':
            write_dimacs(filename)
        else:
            raise ValueError('Incorrect output format')
        
    def generate_vertices(self):
        # vertices
        for v2 in range(self.n2):
            yield ('v', None, v2) # insertions
        for v1 in range(self.n1):
            yield ('v', v1, None) # deletions
            for v2 in range(self.n2):
                yield ('v', v1, v2) # substitutions

        # edges
        for j1 in range(self.n2):
            for j2 in range(j1):
                if self.g2.adjacency_matrix[j1][j2]:
                    yield ('e', None, None, j1, j2) # insertions
        for i1 in range(self.n1):
            for i2 in range(i1):
                if not self.g1.adjacency_matrix[i1][i2]:
                    continue
                yield ('e', i1, i2, None, None) # deletions
                for j1 in range(self.n2):
                    for j2 in range(j1):
                        if self.g2.adjacency_matrix[j1][j2]:
                            yield ('e', i1, i2, j1, j2) # substitutions

    def construct_adjacency_matrix(self):
        adjacency_matrix = []
        for _ in range(self.N):
            adjacency_matrix.append([1] * self.N)
        for i, op1 in enumerate(self.vertices):
            for j, op2 in enumerate(self.vertices):
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

    def generate_weights(self):
        weights = [self.g2.get_vertex_insertion_cost(i) for i in range(self.n2)]
        for i in range(self.n1):
            weights += [self.g1.get_vertex_deletion_cost(i)] + [self.g1.get_vertex_substitution_cost(self.g2, i, j) for j in range(self.n2)]
        weights += [self.g2.get_edge_insertion_cost(i, j) for i in range(self.n2) for j in range(i) if self.g2.adjacency_matrix[i][j]]
        for i1 in range(self.n1):
            for i2 in range(i1):
                if not self.g1.adjacency_matrix[i1][i2]:
                    continue
                weights.append(self.g1.get_edge_deletion_cost(i1, i2))
                for j1 in range(self.n2):
                    for j2 in range(j1):
                        if self.g2.adjacency_matrix[j1][j2]:
                            weights.append(self.g1.get_edge_substitution_cost(self.g2, i1, i2, j1, j2))
        return weights

    def write_dzn(self, filename):
        with open(filename, 'w') as f:
            for i, g in enumerate([self.g1, self.g2])
                f.write('v{} = {};\n'.format(i + 1, g.number_of_vertices))
                f.write('e{} = {};\n'.format(i + 1, g.number_of_edges))
            f.write(dzn_formatting.vector(weights, 'weights'))
            f.write(dzn_formatting.matrix(adjacency_matrix, 'adjacent'))

    def write_dimacs(self, filename):
        e1 = self.g1.number_of_edges
        e2 = self.g2.number_of_edges
        with open(filename, 'w') as f:
            e0 = (n1 + 1) * (n2 + 1) - 1
            f.write('p edge {} {} {} {} {} {}\n'.format(self.N, sum(adjacency_matrix[i][j] for i in range(self.N)
                                                               for j in range(i)), n1, n2, e1, e2))

            for i in range(self.N):
                for j in range(i):
                    if adjacency_matrix[i][j]:
                        f.write('e {} {}\n'.format(i + 1, j + 1))

            for i, w in enumerate(weights):
                f.write('n {} {}\n'.format(i + 1, w))

            # s marks the independent sets that we must choose a vertex from
            for i in range(n1):
                f.write('s {}\n'.format(' '.join([str((i + 1) * (n2 + 1) + j) for j in range(n2 + 1)])))
            for j in range(n2):
                f.write('s {}\n'.format(' '.join([str(i * (n2 + 1) + j + 1) for i in range(n1 + 1)])))
            for i in range(e1):
                f.write('s {}\n'.format(' '.join([str(e0 + (i + 1) * (e2 + 1) + j) for j in range(e2 + 1)])))
            for j in range(e2):
                f.write('s {}\n'.format(' '.join([str(e0 + i * (e2 + 1) + j + 1) for i in range(e1 + 1)])))
