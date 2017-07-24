import csv
from collections import defaultdict
import os
import sys
import subprocess
import common

if len(sys.argv) < 2:
    print('Usage: python <grec/cmu> [5/10/15/20/MIX]')
    exit()

# For each row in the CSV file, generate the DIMACS file, run the max weight clique algorithm, and record results
data = []
with open('graphs/db/{}-GED/{}-low-level-info/{}'.format(
        sys.argv[1].upper(), sys.argv[1].upper(), 'GREC{}-lowlevelinfo.csv'.format(
            sys.argv[2]) if sys.argv[1] == 'grec' else 'CMU-low-level-info.csv')) as csv_file:
    for i, row in enumerate(csv.DictReader(csv_file, delimiter=';')):
        if sys.argv[1] == 'cmu' and i == 0:
            continue
        filename = common.dimacs_filename([row['Graph1 Name'], row['Graph2 Name']], sys.argv[1])
        if not os.path.isfile(filename):
            # generate new data
            subprocess.run(['python', 'convert_grec_to_clique2.py', common.full_path(row['Graph1 Name'], sys.argv[1]),
                            common.full_path(row['Graph2 Name'], sys.argv[1]), 'dimacs'] if sys.argv[1] == 'grec' else
                           ['python', 'convert_cmu.py', common.full_path(row['Graph1 Name'], sys.argv[1]),
                            common.full_path(row['Graph2 Name'], sys.argv[1])])
        print('data generation complete')

        # run the algorithm and record statistics
        process = subprocess.Popen('./max-weight-clique/colour_order -l 1 ' + filename, shell=True, stdout=subprocess.PIPE)
        line = ''
        while not line.startswith("b'Stats"):
            line = str(process.stdout.readline())
        data.append(str(process.stdout.readline()).split())
        print(data[-1])

with open(sys.argv[1] + '.csv', 'w') as f:
    f.write('size,answer,runtime,node_count\n')
    for row in data:
        row[0] = row[0][2:]
        row[-1] = row[-1][:-3]
        f.write(','.join(row) + '\n')
