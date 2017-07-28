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
