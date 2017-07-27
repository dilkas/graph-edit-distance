from collections import namedtuple
from munkres import Munkres
import os
import sys

def initialize_matrix(n):
    matrix = []
    for _ in range(n):
        matrix.append([0] * n)
    return matrix

def full_path(filename, db='grec'):
    return os.path.join('graphs', 'db', db.upper()+'-GED', db.upper(), filename)

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

Parameter = namedtuple('Parameter', ['name', 't', 'mandatory'])
Parameter.__new__.__defaults__ = ('', int, True)


class Script:
    '''A superclass of all scripts, taking care of command-line arguments.'''

    def check_command_line_arguments(self, extra_information=''):
        if len(sys.argv) < len(list(filter(lambda a: a.mandatory, self.parameters))) + self.first_command_line_argument:
            print('Usage: python', ' '.join(sys.argv[i] for i in range(self.first_command_line_argument)),
                  ' '.join(a.name if a.mandatory else '[' + a.name + ']' for a in self.parameters))
            if extra_information:
                print(extra_information)
            exit()

    def __init__(self, first_command_line_argument=2, extra_information=''):
        self.first_command_line_argument = first_command_line_argument
        self.check_command_line_arguments(extra_information)
        self.arguments = {}
        for i, argument in enumerate(sys.argv[first_command_line_argument:]):
            self.arguments[self.parameters[i].name] = self.parameters[i].t(argument);
