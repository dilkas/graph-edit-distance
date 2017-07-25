import subprocess
import sys

# Runs the model on a range of graphs with varying edge probabilities and writes statistics to results.csv file
if len(sys.argv) < 7:
    print('Usage:')
    print('python {} model_file number_of_vertices from to step repeat clique_size'.format(sys.argv[0]))
    print('where (from, to, step) are used just like in range() to generate a sequence of edge probabilities')
    print('and repeat is the number of times to repeat the experiment for each probability')
    print('Example:')
    print('python {} Clique.mzn 50 0.1 1 0.1 3 10'.format(sys.argv[0]))
    exit()

model = sys.argv[1] # Clique.mzn
n = sys.argv[2] # number of vertices
# range for probability
range_from = float(sys.argv[3])
range_to = float(sys.argv[4])
range_step = float(sys.argv[5])
# how many times to repeat for each probability
repeat = int(sys.argv[6])

data = []
p = range_from
while p < range_to:
    local_data = {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
                  'variables': 0, 'propagators': 0, 'propagations': 0,
                  'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
                  'satisfiable': 0}
    for _ in range(repeat):
        # generate a new graph
        arguments = ['python', 'generator.py', n, str(p)]
        if len(sys.argv) > 7:
            arguments.append(sys.argv[7])
        subprocess.run(arguments)

        # run the model and record statistics
        generator = subprocess.Popen('mzn2fzn ' + model + ' generated.dzn',
                                     shell=True, stderr=subprocess.PIPE)
        if str(generator.stderr.readline()).find('WARNING') != -1:
            continue
        process = subprocess.Popen('fzn-gecode -p 8 -s ' +
                                   model[:model.find('.')] + '.fzn', shell=True,
                                   stdout=subprocess.PIPE)
        if str(process.stdout.readline()).find('UNSATISFIABLE') == -1:
            local_data['satisfiable'] += 1
        process.stdout.readline()
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
