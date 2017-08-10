import csv
import os
import sys

with open(os.path.join('graphs', 'db', 'GREC-GED', 'GREC-low-level-info', 'GREC5-lowlevelinfo.csv')) as answers_file:
    answers = dict(((row['Graph1 Name'], row['Graph2 Name']), float(row[' distance'])) for row in csv.DictReader(answers_file, delimiter=';'))

with open(sys.argv[1]) as results:
    for row in csv.DictReader(results):
        if abs(float(row['answer']) - answers[(row['graph1'], row['graph2'])]) >= 0.1:
            sys.exit(1)

