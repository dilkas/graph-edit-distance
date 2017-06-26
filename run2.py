import subprocess
import sys
from timeit import timeit

# Runs the model on a range of graphs with varying edge probabilities and writes statistics to results.csv file
if len(sys.argv) < 9:
    print('Usage:')
    print('python {} model_file n2 edge_probability n1 from to step repeat'.format(sys.argv[0]))
    print('\nn2 (number of vertices), edge_probability describe the smaller graph.')
    print('n1, from, to, step describe the bigger graph,')
    print('where (from, to, step) are used just like in range() to generate a sequence of edge probabilities.')
    print('Repeat is the number of times to repeat the experiment for each probability')
    print('\nExample:')
    print('python {} models/Subgraph.mzn 10 0.5 100 0.01 1 0.01 10'.format(sys.argv[0]))
    exit()

model = sys.argv[1]
n2 = sys.argv[2]
p2 = sys.argv[3] # edge probability
n1 = sys.argv[4]
# range for probability
range_from = float(sys.argv[5])
range_to = float(sys.argv[6])
range_step = float(sys.argv[7])
# how many times to repeat for each probability
repeat = int(sys.argv[8])

data = []
p = range_from
while p < range_to:
    local_data = {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
                  'variables': 0, 'propagators': 0, 'propagations': 0,
                  'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
                  'satisfiable': 0}
    for _ in range(repeat):
        # generate new data
        subprocess.run(['python', 'generator2.py', n1, str(p), n2, p2])

        # run the model and record statistics
        generator = subprocess.Popen('mzn2fzn ' + model + ' generated.dzn',
                                     shell=True, stderr=subprocess.PIPE)
        if str(generator.stderr.readline()).find('WARNING') != -1:
            continue
        process = subprocess.Popen('fzn-gecode -p 9 -s ' +
                                   model[:model.find('.')] + '.fzn', shell=True,
                                   stdout=subprocess.PIPE)
        first_line = str(process.stdout.readline())
        if first_line.find('UNSATISFIABLE') == -1:
            local_data['satisfiable'] += 1
            # test if the isomorphism is injective
            #assert len(set(eval(first_line[first_line.find('['):first_line.find(']') + 1]))) == int(n2), first_line + n2
        process.stdout.readline() # skip a line
        for line in [str(l).split(':') for l in process.stdout]:
            if len(line) > 1:
                name = line[0][4:].lstrip()
                if name.find('time') != -1:
                    local_data[name] += float(line[1].split()[1][1:])
                else:
                    local_data[name] += int(line[1].strip()[:-3])

    # take averages
    for key in local_data:
        local_data[key] = local_data[key] / repeat

    local_data['P'] = p
    data.append(local_data)
    p += range_step

with open('results.csv', 'w') as f:
    f.write(','.join(data[0]) + '\n')
    for row in data:
        f.write(','.join(map(str, row.values())) + '\n')
