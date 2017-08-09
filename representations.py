from collections import namedtuple
import math
from munkres import Munkres
import os
import sys
from xml.etree import ElementTree
import common

def integer_costs_supported(cls):
    '''If the class has an int_version = True attribute, run int() on every number returned by every method starting with "get_"'''
    def decorator(f):
        def wrapper(*args, **kwargs):
            return int(f(*args, **kwargs)) if args[0].int_version == True else f(*args, **kwargs)
        return wrapper
    for attr in cls.__dict__:
        if attr.startswith('get_'):
            setattr(cls, attr, decorator(getattr(cls, attr)))
    return cls


class Representation:

    def __init__(self, data_file, int_version, vertex_properties, edge_properties, index_parser=lambda s: int(s) - 1):
        '''v_properties and e_properties are lists of tuples (n, f), where n is the name of the property and f is a function
        taking an XML node/edge tag and returning the desired property'''
        self.number_of_vertices = 0
        self.number_of_edges = 0
        self.int_version = int_version
        Vertex = namedtuple('Vertex', [p[0] for p in vertex_properties])
        Edge = namedtuple('Edge', [p[0] for p in edge_properties])
        self.vertices = []
        self.adjacency_matrix = []
        self.edges = []

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
                self.vertices.append(Vertex(*[f(element) for _, f in vertex_properties]))
            else:
                self.number_of_edges += 1

                # If this is the first edge, then we know how many vertices there are and we can initialize the matrix
                if self.edges == []:
                    self.edges = common.initialize_matrix(self.number_of_vertices, None)
                    self.adjacency_matrix = common.initialize_matrix(self.number_of_vertices)

                f, t = [index_parser(j) for j in element.attrib.values()]
                self.edges[f][t] = self.edges[t][f] = Edge(*[f(element) for _, f in edge_properties])
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1

    def get_vertex_insertion_cost(self, vertex):
        return self.alpha * self.tau_node

    def get_vertex_deletion_cost(self, i):
        return self.get_vertex_insertion_cost(i)

    def get_edge_deletion_cost(self, i, j):
        return self.get_edge_insertion_cost(i, j)

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        start_freq = len(self.edges[i1][i2].types)
        end_freq = len(other.edges[j1][j2].types)
        if start_freq == 0 or end_freq == 0:
            return 0
        n = start_freq + end_freq
        matrix = common.initialize_matrix(n)
        for i in range(start_freq):
            for j in range(end_freq):
                if self.edges[i1][i2].types[i] != other.edges[j1][j2].types[j]:
                    matrix[i][j] = 2 * self.tau_edge
            for j in range(end_freq, n):
                matrix[i][j] = self.tau_edge if j - end_freq == i else float('inf')
        for i in range(start_freq, n):
            for j in range(end_freq):
                matrix[i][j] = self.tau_edge if i - start_freq == j else float('inf')
        return (1 - self.alpha) * sum([matrix[i][j] for i, j in Munkres().compute(matrix)])


@integer_costs_supported
class Cmu(Representation):
    tau_node = sys.maxsize
    alpha = 0.5

    def __init__(self, data_file, int_version):
        super().__init__(data_file, int_version, [], [('dist', lambda e: float(e[0][0].text))])

    def get_vertex_substitution_cost(self, other, v1, v2):
        return 0

    def get_edge_insertion_cost(self, i, j):
        return (1 - self.alpha) * self.edges[i][j].dist

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return (1 - self.alpha) * abs(self.edges[i1][i2].dist - other.edges[j1][j2].dist)


@integer_costs_supported
class Grec(Representation):
    tau_node = 90
    tau_edge = 15
    alpha = 0.5

    def __init__(self, data_file, int_version):
        super().__init__(data_file, int_version, [('x', lambda e: float(e[0][0].text)), ('y', lambda e: float(e[1][0].text)), ('t', lambda e: e[2][0].text)],
                         [('types', lambda e: [c[0].text for c in e if c.attrib['name'].startswith('type')])], int)

    def get_vertex_substitution_cost(self, other, i, j):
        return (self.alpha * math.sqrt((self.vertices[i].x - other.vertices[j].x)**2 + (self.vertices[i].y - other.vertices[j].y)**2)
                if self.vertices[i].t == other.vertices[j].t else 2 * self.alpha * self.tau_node)

    def get_edge_insertion_cost(self, i, j):
        return (1 - self.alpha) * self.tau_edge * len(self.edges[i][j].types)

@integer_costs_supported
class Muta(Representation):
    tau_node = 11
    tau_edge = 1.1
    alpha = 0.25

    def __init__(self, data_file, int_version):
        super().__init__(data_file, int_version, [('symbol', lambda e: e[0][0].text)], [])

    def get_vertex_insertion_cost(self, vertex):
        return 2 * self.alpha * self.tau_node

    def get_vertex_substitution_cost(self, other, v1, v2):
        return 0 if self.vertices[v1].symbol == other.vertices[v2].symbol else 2 * self.alpha * self.tau_node

    def get_edge_insertion_cost(self, i, j):
        return (1 - self.alpha) * self.tau_edge

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return 0

@integer_costs_supported
class Protein(Representation):
    Vertex = namedtuple('Vertex', ['t', 'sequence'])
    tau_node = 11
    tau_edge = 1
    alpha = 0.75

    def __init__(self, data_file, int_version):
        super().__init__(data_file, int_version, [('t', lambda e: int(e[0][0].text)), ('sequence', lambda e: e[2][0].text)],
                         [('types', lambda e: [c[0].text for c in e if c.attrib['name'].startswith('type')])])

    def get_vertex_substitution_cost(self, other, v1, v2):
        return (self.alpha * self.string_edit_distance(self.vertices[v1].sequence, other.vertices[v2].sequence)
                if self.vertices[v1].t == other.vertices[v2].t else self.alpha * self.tau_node)

    def get_edge_insertion_cost(self, i, j):
        return (1 - self.alpha) * self.tau_edge * len(self.edges[i][j].types)

    def string_edit_distance(self, s1, s2):
        if len(s2) > len(s1):
            s1, s2 = s2, s1
        s2 += s2
        n = len(s1)
        m = len(s2)
        string_matrix = []
        for _ in range(n + 1):
            string_matrix.append([0] * (m + 1))
        for i in range(1, n + 1):
            string_matrix[i][0] = string_matrix[i - 1][0] + self.tau_node

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                subst = 0 if s1[i - 1] == s2[j - 1] else self.tau_node
                m1 = string_matrix[i - 1][j - 1] + subst
                m2 = string_matrix[i - 1][j] + self.tau_node
                m3 = string_matrix[i][j - 1] + self.tau_node
                string_matrix[i][j] = min(m1, m2, m3)

        dmin = float('inf')
        for j in range(m):
            if string_matrix[n][j] < dmin:
                dmin = string_matrix[n][j]
        return dmin
