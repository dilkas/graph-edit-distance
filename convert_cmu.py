import sys
import common
import representations


class CmuToDimacs(common.Script):
    '''Converts CMU GLX files to the DIMACS format for the second clique encoding (with weights only on vertices).'''
    parameters = [common.Parameter('file1'), common.Parameter('file2')]

    def __init__():
        self.check_command_line_arguments()
        g1 = representations.Cmu(sys.argv[2])
        g2 = representations.Cmu(sys.argv[3])
        n1 = len(g1.vertices)
        n2 = len(g2.vertices)

        weights = [sys.maxsize] * n2 # vertex insertions
        for _ in range(n1): # vertex deletion & substitutions
            weights += [sys.maxsize] + [0] * n2
        weights += [0.5 * g2.dist[i][j] for i in range(n2) for j in range(i) if g2.adjacency_matrix[i][j]] # edge insertion
        for i1 in range(n1):
            for i2 in range(i1):
                if not g1.adjacency_matrix[i1][i2]:
                    continue
                weights.append(0.5 * g1.dist[i1][i2]) # edge deletion
                for j1 in range(n2):
                    for j2 in range(j1):
                        if g2.adjacency_matrix[j1][j2]:
                            weights.append(0.5 * abs(g1.dist[i1][i2] - g2.dist[j1][j2]))

        common.output_dimacs(sys.argv[2:], 'cmu', weights)
