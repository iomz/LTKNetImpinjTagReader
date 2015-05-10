#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import inspect
import natsort
import os
import pprint
from re import sub
from sys import exit
import csv

FILE_EXTENSIONS = ('.raw')

def main():
    script_file = inspect.getfile(inspect.currentframe())
    log_directory = os.path.dirname(os.path.abspath(script_file)) + '/logs'

    if not os.path.exists(log_directory):
        print "## '%s' is not a valid path" % log_directory
        sys.exit(0)

    # Array to store tag combinations
    rssis = {}
    total_counts = {}
    
    for root, dirs, files in os.walk(log_directory):
        for f in files:
            # If the file is a final result
            if f.endswith(FILE_EXTENSIONS):
                combination = sub('\.raw', '', f)
                rssis[combination] = []
                total_counts[combination] = 0
                with open(os.path.join(root, f)) as f:
                    for l in f.readlines():
                        # FIXME: array position and total count line
                        if l.startswith('#Summary'):
                            count = l.split()[5][:-1]
                            total_counts[combination] += int(count)
                            continue

                        if l.startswith('#') or l.startswith('PCBits'):
                            continue

                        # should containts = pcbits, rssi, epc, user_memory
                        pcbits, rssi, epc, user_memory = l.split()
                        rssis[combination].append(float(rssi))
                    total_counts[combination] = total_counts[combination]/3.0

    combinations = natsort.natsorted(rssis.keys(), key=lambda c: len(rssis[c]))
    pp = pprint.PrettyPrinter(indent = 2)
    pp.pprint(rssis)

    with open('average_rssi.csv', 'wb') as f:
        writer = csv.writer(f)
        head = ['Combinations', 'Low', 'Open', 'Close', 'High', 'Tooltip', 'Total Read Counts']
        writer.writerow(head)
        for c in combinations:
            low = min(rssis[c])
            high = max(rssis[c])
            avg = reduce(lambda x, y: x + y, rssis[c]) / len(rssis[c])
            tooltip = "Average RSSI is %.2f" % avg
            row = [c, low, avg, avg, high, tooltip, total_counts[c]]
            writer.writerow(row)

if __name__ == "__main__":
    main()

