from collections import defaultdict
import subprocess
import sys
from timeit import timeit

def frange(f, t, s):
    while f < t:
        yield f
        f += s

def initial_data(p, l):
    return {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
            'variables': 0, 'propagators': 0, 'propagations': 0,
            'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
            'answer': 0, 'P': p, 'l': l}

# Runs two models on a range of graphs with varying edge probabilities and writes statistics to results.csv file
if len(sys.argv) < 3:
    print('Usage:')
    print('python {} model1 model2 [repeat]\n'.format(sys.argv[0]))
    exit()

models = sys.argv[1:3]
filenames = ['mcis', 'mc']

# how many times to repeat for each probability
repeat = int(sys.argv[3]) if len(sys.argv) >= 4 else 1

# graph with fixed probabilities
n2 = '15'
p2 = '0.5'
l2 = '0.3'

# graph with varying probabilities
n1 = '15'
p_from = 0.5
p_to = 0.6
p_step = 0.1
l_from = 0.01
l_to = 1
l_step = 0.01

data = defaultdict(list) # a list of results for each model
for p in frange(p_from, p_to, p_step):
    for l in frange(l_from, l_to, l_step):
        for _ in range(repeat):
            # generate new data
            generator = subprocess.run(['python', 'generator4.py', n1, str(p), str(l), n2, p2, l2])

            # run the models and record statistics
            for model, filename in zip(models, filenames):
                local_data = initial_data(p, l)
                if not (filename == 'mc' and generator.returncode == 1):
                    process = subprocess.Popen('mzn-gecode -p 9 -s {} {}'.format(model, filename + '.dzn'), shell=True, stdout=subprocess.PIPE)
                    first_line = process.stdout.readline()
                    if first_line:
                        local_data['answer'] = int(first_line)
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

            # check that the answers are the same
            mcis = data[models[0]][-1]['answer']
            mc = data[models[1]][-1]['answer']
            if mcis != mc:
                print('p = {}, l = {}, MCIS = {}, MC = {}'.format(p, l, mcis, mc))
                exit()

for model, filename in zip(models, filenames):
    with open(filename + '.csv', 'w') as f:
        f.write(','.join(initial_data(0, 0)) + '\n')
        for row in data[model]:
            f.write(','.join(map(str, row.values())) + '\n')
