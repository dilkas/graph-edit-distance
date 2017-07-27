import os
import common
import models
import representations


class Scheduler(common.Script):
    '''Pipe and filter'''
    parameters = [common.Parameter('model', str), common.Parameter('output_format', str), common.Parameter('file1', str),
                  common.Parameter('file2', str), common.Parameter('int_version', str, False)]

    def __init__(self):
        super().__init__(1, """
Supported models: cp, vertex-weights, vertex-edge-weights.
Supported output formats: dzn (for all models), dimacs (for vertex-weights).
To round all numbers to integers, add 'int' at the end""")

        # initialize the graphs
        formats = {'CMU': representations.Cmu, 'GREC': representations.Grec}
        for f in formats:
            if f in self.arguments['file1']:
                if f not in self.arguments['file2']:
                    raise ValueError('The two files should be from the same dataset')
                g1 = formats[f](self.arguments['file1'])
                g2 = formats[f](self.arguments['file2'])
                filename = new_filename(f)
                break
        if 'g1' not in locals():
            raise RuntimeError("I can't figure out which dataset the files are from")

        # create the models
        encodings = {'cp': None, 'vertex-weights': models.VertexWeights, 'vertex-edge-weights': None}
        for model in encodings:
            if self.arguments['model'] == model:
                encodings[model](g1, g2, output_format, filename)

    def new_filename(self, dataset):
        return os.path.join('graphs', self.arguments['output_format'], dataset,
                            '-'.join([os.path.basename(f[:f.rfind('.')]) for f in files]) + '.dzn' if output_format == 'dzn' else '.txt')


if __name__ == '__main__':
    Scheduler()
