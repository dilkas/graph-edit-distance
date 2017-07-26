from collections import namedtuple
import sys
from xml.etree import ElementTree
import common


class Cmu:
    Vertex = namedtuple('Vertex', ['x', 'y'])

    def __init__(self, data_file):
        self.number_of_edges = 0
        self.vertices = [] # a list of vertices
        self.adjacency_matrix = []
        self.dist = [] # a property of all edges

        for element in ElementTree.parse(data_file).getroot()[0]:
            if element.tag == 'node':
                vertices.append(float(self.Vertex(element[0][0].text), float(element[1][0].text)))
            else:
                self.number_of_edges += 1

                # if this is the first edge, then we know how many vertices there are and we can initialize the matrices
                if self.adjacency_matrix == []:
                    self.adjacency_matrix = common.initialize_matrix(len(self.vertices))
                    self.dist = common.initialize_matrix(len(self.vertices))

                f, t = [int(j) - 1 for j in element.attrib.values()]
                self.adjacency_matrix[f][t] = self.adjacency_matrix[t][f] = 1
                self.dist[f][t] = self.dist[t][f] = float(element[0][0].text)
