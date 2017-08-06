import os
import common
import models
import representations


class Scheduler(common.Script):
    parameters = [common.Parameter('model', str), common.Parameter('output_format', str), common.Parameter('file1', str),
                  common.Parameter('file2', str), common.Parameter('int_version', str, False)]

    def __init__(self):
        super().__init__(1, """
Supported models: cp, vertex-weights, vertex-edge-weights.
Supported output formats: dzn (for all models), dimacs (for vertex-weights).
To round all numbers to integers, add 'int' at the end.""")

        # initialize the graphs
        formats = {'CMU': representations.Cmu, 'GREC': representations.Grec, 'Mutagenicity': representations.Muta}
        for f in formats:
            if f in self.arguments['file1']:
                if f not in self.arguments['file2']:
                    raise ValueError('The two files should be from the same dataset')
                g1 = formats[f](self.arguments['file1'], 'int_version' in self.arguments)
                g2 = formats[f](self.arguments['file2'], 'int_version' in self.arguments)
                filename = self.new_filename(f)
                break
        if 'g1' not in locals():
            raise RuntimeError("I can't figure out which dataset the files are from")

        # create the models
        encodings = {'cp': models.ConstraintProgramming, 'vertex-weights': models.VertexWeights, 'vertex-edge-weights': models.VertexEdgeWeights}
        if self.arguments['model'] not in encodings:
            raise ValueError('Incorrect model')

        model = encodings[self.arguments['model']](g1, g2, filename)
        if self.arguments['output_format'] == 'dzn':
            model.write_dzn(filename)
        elif self.arguments['output_format'] == 'dimacs':
            model.write_dimacs(filename)
        else:
            raise ValueError('Incorrect output format')

    def new_filename(self, dataset):
        return os.path.join('graphs', self.arguments['output_format'], self.arguments['model'], dataset,
                            '-'.join([os.path.basename(f[:f.rfind('.')]) for f in [self.arguments['file1'], self.arguments['file2']]]) +
                            ('.dzn' if self.arguments['output_format'] == 'dzn' else '.txt'))


if __name__ == '__main__':
    Scheduler()
