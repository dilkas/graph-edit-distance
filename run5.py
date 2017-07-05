import csv
from collections import defaultdict
import os
import subprocess
import sys
import common

# Takes a CSV results file and a MiniZinc model. For each row in the CSV file, generates the DZN file, runs the model, records results and compares answers

def initial_data():
    return {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
            'variables': 0, 'propagators': 0, 'propagations': 0,
            'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
            'answer': 0.0}

def full_path(filename):
    return os.path.join('graphs', 'db', 'GREC-GED', 'GREC', filename)

if len(sys.argv) < 3:
    print('Usage: python {} csv_file model'.format(sys.argv[0]))

data = []
with open(sys.argv[1]) as csv_file:
    for row in csv.DictReader(csv_file, delimiter=';'):
        if not os.path.isfile(common.new_filename([row['Graph1 Name'], row['Graph2 Name']])):
            # generate new data
            subprocess.run(['python', 'convert_grec.py', full_path(row['Graph1 Name']), full_path(row['Graph2 Name'])])

        # run the model and record statistics
        local_data = initial_data()
        process = subprocess.Popen('mzn-gecode -p 9 -s {} {}'.format(sys.argv[2], common.new_filename([row['Graph1 Name'], row['Graph2 Name']])),
                                   shell=True, stdout=subprocess.PIPE)
        for _ in range(3):
            first_line = str(process.stdout.readline())
            print(first_line)
        local_data['answer'] = float(first_line[first_line.find('=') + 2:-4])
        process.stdout.readline() # skip a line
        for line in [str(l).split(': ') for l in process.stdout]:
            if len(line) <= 1:
                continue
            name = line[0][4:].lstrip()
            if name.find('time') != -1:
                local_data[name] += float(line[1].split()[1][1:])
            else:
                local_data[name] += int(line[1].strip()[:-3])
        data.append(local_data)

        # check that the answers are the same
        if abs(float(row[' distance']) - local_data['answer']) > 1:
            if float(row[' distance']) - local_data['answer'] < -1:
                print('my answer is higher')
                if float(row[' distance']) - local_data['answer'] > 1:
                    print('my answer is lower')
            print('row:', row)
            print('distance:', local_data['answer'])

with open('results.csv', 'w') as f:
    f.write(','.join(initial_data()) + '\n')
    for row in data:
        f.write(','.join(map(str, row.values())) + '\n')
