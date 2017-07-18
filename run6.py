import csv
from collections import defaultdict
import os
import subprocess
import common

# For each row in the CSV file, generate the DIMACS file, run the max weight clique algorithm, and record results
data = []
with open('graphs/db/GREC-GED/GREC-low-level-info/GREC10-lowlevelinfo.csv') as csv_file:
    for row in csv.DictReader(csv_file, delimiter=';'):
        filename = common.new_filename([row['Graph1 Name'], row['Graph2 Name']], 'dimacs2')
        if not os.path.isfile(filename):
            # generate new data
            subprocess.run(['python', 'convert_grec_to_clique2.py', common.full_path(row['Graph1 Name']),
                            common.full_path(row['Graph2 Name']), 'dimacs', 'int'])

        # run the algorithm and record statistics
        process = subprocess.Popen('./max-weight-clique/colour_order ' + filename, shell=True, stdout=subprocess.PIPE)
        line = ''
        while not line.startswith("b'Stats"):
            line = str(process.stdout.readline())
        data.append(str(process.stdout.readline()).split())
        print(data[-1])

with open('mwc.csv', 'w') as f:
    f.write('size,answer,runtime,node_count\n')
    for row in data:
        row[0] = row[0][2:]
        row[-1] = row[-1][:-3]
        f.write(','.join(row) + '\n')
