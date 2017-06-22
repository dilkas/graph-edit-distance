import subprocess
import sys
from timeit import timeit

# Prints the average running time for each edge probability in a CSV format
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

p = range_from
x_values = []
y_values = []
satisfiable = []
while p < range_to:
    x_values.append(p)
    s = 0
    satisfiable_count = 0
    for _ in range(repeat):
        arguments = ['python', 'generator.py', n, str(p)]
        if len(sys.argv) > 7:
            arguments.append(sys.argv[7])
        subprocess.run(arguments)
        process = subprocess.Popen('/usr/bin/time -f "%e" mzn-gecode -p 8 ' + model + ' generated.dzn',
                                   shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if str(process.stdout.readline()).find('UNSATISFIABLE') == -1:
            satisfiable_count += 1
        # backend solvers print warnings for inconsistent models, but we want to process them anyway
        for line in process.stderr:
            try:
                s += float(line)
            except Exception:
                pass
    y_values.append(s / repeat)
    satisfiable.append(satisfiable_count)
    p += range_step

with open('results.csv', 'w') as f:
    f.write('P,t,times_satisfiable\n')
    for x, y, s in zip(x_values, y_values, satisfiable):
        f.write('{},{},{}\n'.format(x, y, s))
