from collections import defaultdict
import subprocess
import sys

Graph = namedtuple('Graph', ['number_of_vertices', 'edge_probability', 'label_probability'])
Graph.__new__.__defaults__ = (None, None, None)

def frange(f, t, s):
    while f < t:
        yield f
        f += s

def initial_data(p=-1, l=-1):
    # -1 means "not applicable" (if a model failed or a parameter is unused)
    return {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
            'variables': 0, 'propagators': 0, 'propagations': 0,
            'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
            'answer': -1, 'satisfiable': 0, 'P': p, 'l': l}

def run_generator():
    # TODO: start here
    subprocess.run(['python', 'generator.py', problem_name])

def run(model, data_file, results):
    process = subprocess.Popen(model + ' ' + data_file, shell=True, stdout=subprocess.PIPE)
    if 'UNSATISFIABLE' not in str(process.stdout.readline()):
        results['satisfiable'] = 1
    process.stdout.readline()
    for line in [str(l).split(':') for l in process.stdout]:
        if len(line) > 1:
            local_data[line[0][4:].lstrip()] = float(line[1].split()[1][1:]) if 'time' in name else int(line[1].strip()[:-3])

########## PARAMETERS ##########

gecode_prefix = 'mzn-gecode -p 9 -s '
models = [gecode_prefix + 'models/Clique.mzn'] # A list of commands to run on each graph ( a filename is added before running)
repeat = 1 # How many times to repeat each run
csv_file = '' # For the "low level info" files. Set to empty string to run the generator instead
int_version = False

# Parameters for graph generation
problem_name = 'clique' # the first argument for generator.py
# Set up graph1 and graph2 for the problem. If the problem is defined for a single graph, graph2 is ignored.
# Edge_probability and label_probability can be either static values or calls to frange()
graph1 = Graph(10, frange(0.1, 1, 0.1))

################################

results = defaultdict(list)
for model in models:
    for p in p_range:
        local_data = initial_data()
        for _ in range(repeat):
            run_generator()
            run(model, ???, local_data)
        local_data['P'] = p
        data.append(local_data)

with open('results.csv', 'w') as f:
    f.write(','.join(data[0]) + '\n')
    for row in data:
        f.write(','.join(map(str, row.values())) + '\n')
