import csv
from collections import defaultdict
import os
import subprocess
import sys
import common

# Takes a CSV results file and a MiniZinc model. For each row in the CSV file, generates the DZN file, runs the models, records results and compares answers

def initial_data():
    return {'runtime': 0.0, 'solvetime': 0.0, 'solutions': 0,
            'variables': 0, 'propagators': 0, 'propagations': 0,
            'nodes': 0, 'failures': 0, 'restarts': 0, 'peak depth': 0,
            'answer': 0.0}

def full_path(filename):
    return os.path.join('graphs', 'db', 'GREC-GED', 'GREC', filename)

data = [[], [], []]
models = ['ged', 'clique1', 'clique2']
model_filenames = map(lambda x: os.path.join('models', x), ['GraphEditDistance3.mzn', 'MaximumWeightClique.mzn', 'MaximumWeightClique2.mzn'])

for i, (model, filename) in enumerate(zip(models, model_filenames)):
    with open(os.path.join('graphs', 'db', 'GREC-GED', 'GREC-low-level-info', 'GREC5-lowlevelinfo.csv')) as csv_file:
        for row in csv.DictReader(csv_file, delimiter=';'):
            data_file = common.new_filename([row['Graph1 Name'], row['Graph2 Name']], model)
            if not os.path.isfile(data_file):
                # generate new data
                subprocess.run(['python', 'convert_grec_to_{}.py'.format(model),
                                full_path(row['Graph1 Name']), full_path(row['Graph2 Name'])])

            # run the model and record statistics
            local_data = initial_data()
            process = subprocess.Popen('mzn-gecode -s {} {}'.format(filename, data_file), shell=True, stdout=subprocess.PIPE)
            #print(row)
            skip = False
            for _ in range(3 if model == 'ged' else 2):
                # adding 'output' lines to MiniZinc models sometimes causes them to produce wrong answers,
                # so we just skip the lines we are not interested in (or print them for debugging purposes)
                first_line = str(process.stdout.readline())
                if first_line.find('UNSATISFIABLE') != -1:
                    skip = True
                    break
            if skip:
                continue
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
            data[i].append(local_data)
            if abs(abs(local_data['answer']) - float(row[' distance'])) > 1:
                print(model, 'is wrong')

    with open('{}_results.csv'.format(model), 'w') as f:
        f.write(','.join(initial_data()) + '\n')
        for row in data[i]:
            f.write(','.join(map(str, row.values())) + '\n')
