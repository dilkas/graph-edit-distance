from collections import defaultdict
import subprocess
import sys
from timeit import timeit

def initial_data(p):
    return {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
            'variables': 0, 'propagators': 0, 'propagations': 0,
            'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
            'answer': 0, 'P': p}

# Runs two models on a range of graphs with varying edge probabilities and writes statistics to results.csv file
if len(sys.argv) < 10:
    print('Usage:')
    print('python {} model1 model2 n2 edge_probability n1 from to step repeat\n'.format(sys.argv[0]))

    print('n2 (number of vertices), edge_probability describe the smaller graph.')
    print('n1, from, to, step describe the bigger graph,')
    print('where (from, to, step) are used just like in range() to generate a sequence of edge probabilities.')
    print('Repeat is the number of times to repeat the experiment for each probability\n')

    print('Example:')
    print('python {} models/CommonInducedSubgraph.mzn models/Clique.mzn 10 0.5 100 0.01 1 0.01 10'.format(sys.argv[0]))
    exit()

models = sys.argv[1:3]
filenames = ['mcis', 'mc']

# graph with fixed edge probability
n2 = sys.argv[3]
p2 = sys.argv[4]

# graph with varying edge probability
n1 = sys.argv[5]
range_from = float(sys.argv[6])
range_to = float(sys.argv[7])
range_step = float(sys.argv[8])

# how many times to repeat for each probability
repeat = int(sys.argv[9])

data = defaultdict(list) # a list of results for each model
# generate new data
subprocess.run(['python', 'generator3.py', n1, str(p), n2, p2])

# run the models and record statistics
for model, filename in zip(models, filenames):
    local_data['answer'] = int(process.stdout.readline())
    process.stdout.readline() # skip a line
    for line in [str(l).split(': ') for l in process.stdout]:
        if len(line) <= 1:
            continue
        name = line[0][4:].lstrip()
        if name.find('time') != -1:
            local_data[name] += float(line[1].split()[1][1:])
        else:
            local_data[name] += int(line[1].strip()[:-3])
    data[model].append(local_data)

for model, filename in zip(models, filenames):
    with open(filename + '.csv', 'w') as f:
        f.write(','.join(initial_data(0)) + '\n')
        for row in data[model]:
            f.write(','.join(map(str, row.values())) + '\n')
