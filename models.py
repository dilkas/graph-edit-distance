from collections import namedtuple
import itertools
import dzn_formatting


class Model:

    def __init__(self, g1, g2, filename):
        self.g1 = g1
        self.g2 = g2
        self.n1 = g1.number_of_vertices
        self.n2 = g2.number_of_vertices

    def generate_vertex_operation_costs(self):
        weights = [self.g2.get_vertex_insertion_cost(i) for i in range(self.n2)]
        for i in range(self.n1):
            weights += [self.g1.get_vertex_deletion_cost(i)] + [self.g1.get_vertex_substitution_cost(self.g2, i, j) for j in range(self.n2)]
        return weights


class CliqueModel(Model):

    def __init__(self, g1, g2, filename):
        super().__init__(g1, g2, filename)
        self.vertices = list(self.generate_vertices())
        self.N = len(self.vertices)
        self.adjacency_matrix = self.construct_adjacency_matrix()
        self.weights = self.generate_weights()

    def write_dimacs(self, filename):
        raise RuntimeError('DIMACS output format is not supported for this model')


class VertexWeights(CliqueModel):
    '''Takes two graphs and encodes a graph edit distance problem between them as a clique with weights on vertices only'''

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
        weights = self.generate_vertex_operation_costs()
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
            for i, g in enumerate([self.g1, self.g2]):
                f.write('v{} = {};\n'.format(i + 1, g.number_of_vertices))
                f.write('e{} = {};\n'.format(i + 1, g.number_of_edges))
            f.write(dzn_formatting.vector(self.weights, 'weights'))
            f.write(dzn_formatting.matrix(self.adjacency_matrix, 'adjacent'))

    def write_dimacs(self, filename):
        e1 = self.g1.number_of_edges
        e2 = self.g2.number_of_edges
        with open(filename, 'w') as f:
            e0 = (self.n1 + 1) * (self.n2 + 1) - 1
            f.write('p edge {} {} {} {} {} {}\n'.format(self.N, sum(self.adjacency_matrix[i][j] for i in range(self.N)
                                                                    for j in range(i)), self.n1, self.n2, e1, e2))

            for i in range(self.N):
                for j in range(i):
                    if self.adjacency_matrix[i][j]:
                        f.write('e {} {}\n'.format(i + 1, j + 1))

            for i, w in enumerate(self.weights):
                f.write('n {} {}\n'.format(i + 1, w))

            # s marks the independent sets that we must choose a vertex from
            for i in range(self.n1):
                f.write('s {}\n'.format(' '.join([str((i + 1) * (self.n2 + 1) + j) for j in range(self.n2 + 1)])))
            for j in range(self.n2):
                f.write('s {}\n'.format(' '.join([str(i * (self.n2 + 1) + j + 1) for i in range(self.n1 + 1)])))
            for i in range(e1):
                f.write('s {}\n'.format(' '.join([str(e0 + (i + 1) * (e2 + 1) + j) for j in range(e2 + 1)])))
            for j in range(e2):
                f.write('s {}\n'.format(' '.join([str(e0 + i * (e2 + 1) + j + 1) for i in range(e1 + 1)])))


class VertexEdgeWeights(CliqueModel):
    '''Takes two graphs and encodes a graph edit distance problem between them as a clique with weights on vertices and edges'''

    def generate_vertices(self):
        for v2 in range(self.n2):
            yield ('insertion', None, v2)
        for v1 in range(self.n1):
            yield ('deletion', v1, None)
            for v2 in range(self.n2):
                yield ('substitution', v1, v2)

    def construct_adjacency_matrix(self):
        adjacency_matrix = []
        for op1 in self.vertices:
            row = []
            for op2 in self.vertices:
                row.append(0 if op1[1] == op2[1] != None or op1[2] == op2[2] != None else 1)
            adjacency_matrix.append(row)
        return adjacency_matrix

    def generate_weights(self):
        Weights = namedtuple('Weights', ['vertex', 'edge'])
        weights = Weights(self.generate_vertex_operation_costs(), [])
        for op1 in self.vertices:
            row = []
            for op2 in self.vertices:
                if op1[0] == 'insertion':
                    if op2 == op1 or op2[0] == 'deletion' or op2[0] == 'substitution' and op2[2] == op1[2]:
                        row.append(0)
                    elif op2[0] != 'deletion':
                        row.append(self.g2.get_edge_insertion_cost(op1[2], op2[2]) if self.g2.adjacency_matrix[op1[2]][op2[2]] else 0)
                    else:
                        raise RuntimeError('This should never happen')
                elif op1[0] == 'deletion':
                    if op2[0] == 'insertion' or op2 == op1 or op2[0] == 'substitution' and op2[1] == op1[1]:
                        row.append(0)
                    elif op2[0] != 'insertion':
                        row.append(self.g1.get_edge_deletion_cost(op1[1], op2[1]) if self.g1.adjacency_matrix[op1[1]][op2[1]] else 0)
                    else:
                        raise RuntimeError('This should never happen')
                else:
                    if (op2[0] == 'substitution' and (op2[1] == op1[1] or op2[2] == op1[2]) or
                        op2[0] == 'insertion' and op2[2] == op1[2] or op2[0] == 'deletion' and op2[1] == op1[1]):
                        row.append(0)
                    elif op2[0] == 'substitution':
                        if not self.g1.adjacency_matrix[op1[1]][op2[1]] and self.g2.adjacency_matrix[op1[2]][op2[2]]:
                            row.append(self.g2.get_edge_insertion_cost(op1[2], op2[2]))
                        elif self.g1.adjacency_matrix[op1[1]][op2[1]] and not self.g2.adjacency_matrix[op1[2]][op2[2]]:
                            row.append(self.g1.get_edge_deletion_cost(op1[1], op2[1]))
                        else:
                            row.append(min(self.g1.get_edge_substitution_cost(self.g2, op1[1], op2[1], op1[2], op2[2]),
                                           self.g1.get_edge_deletion_cost(op1[1], op2[1]) + self.g2.get_edge_insertion_cost(op1[2], op2[2])))
                    else:
                        row.append(self.g2.get_edge_insertion_cost(op1[2], op2[2]) if op2[0] == 'insertion' else
                                   self.g1.get_edge_deletion_cost(op1[1], op2[1]))
            weights.edge.append(row)
        return weights

    def write_dzn(self, filename):
        with open(filename, 'w') as f:
            for i, g in enumerate([self.g1, self.g2]):
                f.write('v{} = {};\n'.format(i + 1, g.number_of_vertices))
            f.write(dzn_formatting.vector(self.weights.vertex, 'vertexWeights'))
            f.write(dzn_formatting.matrix(self.weights.edge, 'edgeWeights'))
            f.write(dzn_formatting.matrix(self.adjacency_matrix, 'adjacent'))


class ConstraintProgramming(Model):
    '''Takes two graphs and encodes a graph edit distance problem between them as a CP model for MiniZinc'''

    def write_dzn(self, filename):
        with open(filename, 'w') as f:
            for i, g in enumerate([self.g1, self.g2]):
                f.write('n{} = {};\n'.format(i + 1, g.number_of_vertices))
                f.write(dzn_formatting.matrix(g.adjacency_matrix, 'adjacent{}'.format(i + 1)))

            # vertex operation costs
            costs = self.generate_vertex_operation_costs()
            f.write(dzn_formatting.vector(costs[:self.n2], 'vertexInsertionCost'))
            # deletion costs are encoded as the first column of the substitution cost matrix
            f.write(dzn_formatting.two_dimensions(costs[self.n2:], 'vertexSubstitutionCost'))

            # edge insertions & deletions
            edge_ops = [[], []]
            names = ['edgeDeletionCost', 'edgeInsertionCost']
            for i, (num_vertices, cost_function) in enumerate([(self.n1, self.g1.get_edge_deletion_cost), (self.n2, self.g2.get_edge_insertion_cost)]):
                for j in range(num_vertices):
                    edge_ops[i].append([cost_function(j, k) for k in range(num_vertices)])
                f.write(dzn_formatting.matrix(edge_ops[i], names[i]))

            # edge substitutions
            f.write(dzn_formatting.four_dimensions([self.g1.get_edge_substitution_cost(self.g2, i, j, k, l)
                                                    for i, k, j, l in itertools.product(range(self.n1), range(self.n2), repeat=2)], 'edgeSubstitutionCost'))
