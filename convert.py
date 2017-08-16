import os
import sys
import common
import models
import representations


class Scheduler(common.Script):
    parameters = [common.Parameter('model', str), common.Parameter('output_format', str), common.Parameter('file1', str),
                  common.Parameter('file2', str)]

    def __init__(self):
        super().__init__(1, """
Supported models: cp, vertex-weights, vertex-edge-weights.
Supported output formats: dzn (for all models), dimacs (for vertex-weights).
To round all numbers to integers, add 'int' as an extra argument.
To use a different file extension, provide it as an extra argument.""")

        # initialize the graphs
        formats = {'CMU': representations.Cmu, 'GREC': representations.Grec, 'Mutagenicity': representations.Muta, 'Protein': representations.Protein}
        for f in formats:
            if f in self.arguments['file1']:
                if f not in self.arguments['file2']:
                    raise ValueError('The two files should be from the same dataset')
                int_version = 'int' in self.optional_parameters()
                g1 = formats[f](self.arguments['file1'], int_version)
                g2 = formats[f](self.arguments['file2'], int_version)
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

    def optional_parameters(self):
        return sys.argv[len(self.parameters) + 1:]

    def new_filename(self, dataset):
        extension = 'dzn' if self.arguments['output_format'] == 'dzn' else 'txt'
        for arg in self.optional_parameters():
            if arg != 'int':
                extension = arg.strip()
                break
        return os.path.join('graphs', self.arguments['output_format'], self.arguments['model'], dataset,
                            '-'.join([os.path.basename(f[:f.rfind('.')]) for f in [self.arguments['file1'],
                                                                                   self.arguments['file2']]]) + '.' + extension)


if __name__ == '__main__':
    Scheduler()
