from collections import namedtuple
import math
import os
import sys
from xml.etree import ElementTree
import common


class Representation:
    def __init__(self):
        self.number_of_vertices = 0
        self.number_of_edges = 0
        self.adjacency_matrix = []


class Cmu(Representation):
    def __init__(self, data_file):
        super().__init__()
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


class Grec(Representation):
    Vertex = namedtuple('Vertex', ['x', 'y', 't'])

    def __init__(self, data_file):
        super().__init__()
        self.vertices = [] # a list of all vertices
        self.edge_types = [] # each edge has a list of types

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                self.number_of_vertices += 1
                self.vertices.append(Vertex(float(element[0][0].text), float(element[1][0].text), element[2][0].text))
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
                if self.vertices[i].t == other.vrtices[j].t else 90)

    def get_edge_insertion_cost(self, i, j):
        return 7.5 * len(self.edge_types[i][j])

    def get_edge_deletion_cost(self, i, j):
        return 7.5 * len(self.edge_types[i][j])

    def get_edge_substitution_cost(self, other, i1, i2, j1, j2):
        return (common.edge_substitution_cost(self.edge_types[i1][i2], other.edge_types[j1][j2])
                if len(self.edge_types[i1][i2]) != 0 and len(other.edge_types[j1][j2]) != 0 else 0)
