#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import inspect
import natsort
import os
import pprint
from math import sqrt
from re import sub
from sys import argv, exit

FILE_EXTENSION = '.raw'

def main():
    if len(argv) != 2:
        print "Usage: %s <file>" % argv[0]
        exit(0)

    log_file = argv[1]

    if not os.path.exists(log_file) or not log_file.endswith(FILE_EXTENSION):
        print "## '%s' is not a valid file" % log_file
        exit(0)

    # Array to store tag combinations
    combination = sub(FILE_EXTENSION, '', log_file.split('/')[-1])
    rssis = {}
    
    with open(log_file) as f:
        for l in f.readlines():
            # FIXME: array position and total count line
            if l.startswith('#') or l.startswith('PCBits'):
                continue

            # should containts = pcbits, rssi, tag, user_memory
            pcbits, rssi, tag, user_memory = l.split()
            if tag not in rssis:
                rssis[tag] = []
            rssis[tag].append(float(rssi))

    tags = natsort.natsorted(rssis.keys(), key=lambda t: rssis[t])
    pp = pprint.PrettyPrinter(indent = 2)
    pp.pprint(tags)
    pp.pprint(rssis)

    with open(combination + '_rssi.csv', 'wb') as f:
        writer = csv.writer(f)
        head = ['Tags', 'Low', 'Open', 'Close', 'High', 'Tooltip', 'Total Read Counts']
        writer.writerow(head)
        for t in tags:
            low = min(rssis[t])
            high = max(rssis[t])
            mean = reduce(lambda x, y: x + y, rssis[t]) / len(rssis[t])
            tmp = 0
            for r in rssis[t]:
                tmp += (float(r) - mean)**2
            variance = sqrt(tmp/len(rssis[t]))
            tooltip = "Average RSSI is %.2f " % mean
            row = [t, low, mean - variance, mean + variance, high, tooltip, len(rssis[t])]
            writer.writerow(row)

if __name__ == "__main__":
    main()

