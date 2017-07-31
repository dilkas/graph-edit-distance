from collections import defaultdict
import subprocess
import sys

Graph = namedtuple('Graph', ['number_of_vertices', 'edge_probability', 'label_probability'])
Graph.__new__.__defaults__ = (None, None, None)

def run(model, data_file, results):
    for line in [str(l).split(':') for l in process.stdout]:
        if len(line) > 1:
            local_data[line[0][4:].lstrip()] = float(line[1].split()[1][1:]) if 'time' in name else int(line[1].strip()[:-3])

# Set up graph1 and graph2 for the problem. If the problem is defined for a single graph, graph2 is ignored.
# Edge_probability and label_probability can be either static values or calls to frange()
graph1 = Graph(10, frange(0.1, 1, 0.1))

results = defaultdict(list)
        for _ in range(repeat):
            run(model, ???, local_data)
        data.append(local_data)

with open('results.csv', 'w') as f:
    f.write(','.join(data[0]) + '\n')
    for row in data:
        f.write(','.join(map(str, row.values())) + '\n')
