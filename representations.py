from collections import namedtuple
import math
from munkres import Munkres
import os
import sys
from xml.etree import ElementTree
import common

def integer_costs_supported(cls):
    def decorator(f):
        def wrapper(*args, **kwargs):
            return int(f(*args, **kwargs)) if args[0].int_version == True else f(*args, **kwargs)
        return wrapper
    for attr in cls.__dict__:
        if attr.startswith('get_'):
            setattr(cls, attr, decorator(getattr(cls, attr)))
    return cls


class Representation:

    def __init__(self, int_version):
        self.number_of_vertices = 0
        self.number_of_edges = 0
        self.adjacency_matrix = []
        self.int_version = int_version


@integer_costs_supported
class Cmu(Representation):
    def __init__(self, data_file, int_version):
        super().__init__(int_version)
        self.dist = [] # a property of all edges

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
            else:
                self.number_of_edges += 1

                # if this is the first edge, then we know how many vertices there are and we can initialize the matrices
                if self.adjacency_matrix == []:
                    self.adjacency_matrix = common.initialize_matrix(self.number_of_vertices)
                    self.dist = common.initialize_matrix(self.number_of_vertices)

                f, t = [int(j) - 1 for j in element.attrib.values()]
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1
                self.dist[f][t] = self.dist[t][f] = float(element[0][0].text)

    def get_vertex_insertion_cost(self, vertex):
        return sys.maxsize

    def get_vertex_deletion_cost(self, vertex):
        return sys.maxsize

    def get_vertex_substitution_cost(self, other, v1, v2):
        return 0

    def get_edge_insertion_cost(self, i, j):
        return 0.5 * self.dist[i][j]

    def get_edge_deletion_cost(self, i, j):
        return 0.5 * self.dist[i][j]

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return 0.5 * abs(self.dist[i1][i2] - other.dist[j1][j2])


@integer_costs_supported
class Grec(Representation):
    Vertex = namedtuple('Vertex', ['x', 'y', 't'])

    def __init__(self, data_file, int_version):
        super().__init__(int_version)
        self.vertices = [] # a list of all vertices
        self.edge_types = [] # each edge has a list of types

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
                self.vertices.append(self.Vertex(float(element[0][0].text), float(element[1][0].text), element[2][0].text))
            else:
                self.number_of_edges += 1

                # if this is the first edge, then we know how many vertices there are and we can initialize the matrices
                if self.adjacency_matrix == []:
                    self.adjacency_matrix = common.initialize_matrix(self.number_of_vertices)
                    for _ in range(self.number_of_vertices):
                        self.edge_types.append([[] for _ in range(self.number_of_vertices)])

                f, t = [int(j) for j in element.attrib.values()]
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1
                self.edge_types[f][t] = self.edge_types[t][f] = [child[0].text for child in element if child.attrib['name'].startswith('type')]

    def get_vertex_insertion_cost(self, vertex):
        return 45

    def get_vertex_deletion_cost(self, vertex):
        return 45

    def get_vertex_substitution_cost(self, other, i, j):
        return (0.5 * math.sqrt((self.vertices[i].x - other.vertices[j].x)**2 + (self.vertices[i].y - other.vertices[j].y)**2)
                if self.vertices[i].t == other.vertices[j].t else 90)

    def get_edge_insertion_cost(self, i, j):
        return 7.5 * len(self.edge_types[i][j])

    def get_edge_deletion_cost(self, i, j):
        return 7.5 * len(self.edge_types[i][j])

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        start_freq = len(self.edge_types[i1][i2])
        end_freq = len(other.edge_types[j1][j2])
        if start_freq == 0 or end_freq == 0:
            return 0
        n = start_freq + end_freq
        matrix = common.initialize_matrix(n)
        for i in range(start_freq):
            for j in range(end_freq):
                if self.edge_types[i] != other.edge_types[j]:
                    matrix[i][j] = 30
            for j in range(end_freq, n):
                matrix[i][j] = 15 if j - end_freq == i else float('inf')
        for i in range(start_freq, n):
            for j in range(end_freq):
                matrix[i][j] = 15 if i - start_freq == j else float('inf')
        return 0.5 * sum([matrix[i][j] for i, j in Munkres().compute(matrix)])

@integer_costs_supported
class Muta(Representation):
    def __init__(self, data_file, int_version):
        super().__init__(int_version)
        self.symbols = [] # a property of all vertices

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
                self.symbols.append(element[0][0].text)
            else:
                self.number_of_edges += 1

                # if this is the first edge, then we know how many vertices there are and we can initialize the matrix
                if self.adjacency_matrix == []:
                    self.adjacency_matrix = common.initialize_matrix(self.number_of_vertices)

                f, t = [int(j) - 1 for j in element.attrib.values()]
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1

    def get_vertex_insertion_cost(self, vertex):
        return 5.5

    def get_vertex_deletion_cost(self, vertex):
        return 5.5

    def get_vertex_substitution_cost(self, other, v1, v2):
        return 0 if self.symbols[v1] == other.symbols[v2] else 5.5

    def get_edge_insertion_cost(self, i, j):
        return 0.825

    def get_edge_deletion_cost(self, i, j):
        return 0.825

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return 0

@integer_costs_supported
class Protein(Representation):
    Vertex = namedtuple('Vertex', ['type', 'sequence'])

    def __init__(self, data_file, int_version):
        super().__init__(int_version)
        self.vertices = [] # a list of all vertices

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
                self.vertices.append(self.Vertex(int(element[0][0]), element[1][0]))
            else:
                self.number_of_edges += 1

                # if this is the first edge, then we know how many vertices there are and we can initialize the matrix
                if self.adjacency_matrix == []:
                    self.adjacency_matrix = common.initialize_matrix(self.number_of_vertices)

                f, t = [int(j) - 1 for j in element.attrib.values()]
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1

    def get_vertex_insertion_cost(self, vertex):
        return 5.5

    def get_vertex_deletion_cost(self, vertex):
        return 5.5

    def get_vertex_substitution_cost(self, other, v1, v2):
        return 0 if self.symbols[v1] == other.symbols[v2] else 5.5

    def get_edge_insertion_cost(self, i, j):
        return 0.825

    def get_edge_deletion_cost(self, i, j):
        return 0.825

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return 0
