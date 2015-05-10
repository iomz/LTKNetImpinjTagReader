#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import inspect
import natsort
import os
import pprint
from re import sub
from sys import exit
import csv

FILE_EXTENSIONS = ('.tmp', '.raw', '.csv')
ABSTRACT_NAME = True

class PCBits(object):
    PCBITS_LENGTH = 16

    def __init__(self, pcbits):
        self.epc_length = ((pcbits & 0b1111100000000000) >> 11)*16
        self.nsi = (pcbits & 0b0000000100000000) >> 8
        self.afi = (pcbits & 0b0000000011111111)

def get_iso_from_afi(afi):
    AFIs = {\
        "17363_ISO" : 0xA1,
        "17365_ISO" : 0xA2,
        "17364_ISO" : 0xA3,
        "17367_HazMat" : 0xA4,
        "17366_ISO" : 0xA5,
        "17366_HazMat" : 0xA6,
        "17365_HazMat" : 0xA7,
        "17364_HazMat" : 0xA8,
        "17363_ISO" : 0xA9,
        "17363_HazMat" : 0xAA
    }
    if afi in AFIs.values():
        for k,v in AFIs.iteritems():
            if v == afi:
                return k
    return None
    
def main():
    script_file = inspect.getfile(inspect.currentframe())
    log_directory = os.path.dirname(os.path.abspath(script_file)) + '/logs'

    if not os.path.exists(log_directory):
        print "## '%s' is not a valid path" % log_directory
        sys.exit(0)

    # Array to store tag combinations
    counts = {}
    tags = []
    if ABSTRACT_NAME:
        abst_tags = {}
    
    for root, dirs, files in os.walk(log_directory):
        for combination in files:
            # If the file is a final result
            if not combination.endswith(FILE_EXTENSIONS):
                counts[combination] = {}
                with open(os.path.join(root, combination)) as f:
                    for l in f.readlines():
                        # should containts = count, rssi, tag, pcbits
                        count, rssi, tag, pcbits = l.split()
                        pc = PCBits(int(pcbits, 10))
                        if pc.nsi == 0 and pc.epc_length == 96: # GS1
                            standard = "GS1"
                        elif pc.nsi == 1 and 0xA1 <= pc.afi <= 0xAA: # ISO
                            standard = get_iso_from_afi(pc.afi)
                        else:
                            standard = "PROPRIETARY"

                        if ABSTRACT_NAME:
                            # name tag
                            tag_type = None
                            if tag in abst_tags:
                                tag_type = abst_tags[tag]
                            else:
                                for i in range(1000):
                                    tag_type = standard + '_' + str(i)
                                    if tag_type not in abst_tags.values():
                                        abst_tags[tag] = tag_type
                                        break
                            counts[combination][tag_type] = count
                        else:
                            counts[combination][tag] = count

                        if tag not in tags:
                            tags.append(tag)

    combinations = natsort.natsorted(counts.keys(), key=lambda c: len(counts[c]))
    if ABSTRACT_NAME:
        tags = natsort.natsorted(abst_tags.values(), key=lambda t: t.lower())
    else:
        tags = natsort.natsorted(tags, key=lambda t: t.lower())
    pp = pprint.PrettyPrinter(indent = 2)
    pp.pprint(combinations)
    pp.pprint(tags)
    pp.pprint(abst_tags)
    pp.pprint(counts)

    with open('ro_access_report_counts.csv', 'wb') as f:
        writer = csv.writer(f)
        head = ['Tag']
        if ABSTRACT_NAME:
            head += [sub('_[0-9]+', '', a) for a in tags]
        else:
            head += tags
        head.append('Total')
        writer.writerow(head)
        for c in combinations:
            row = [c]
            count_sum = 0
            for t in tags:
                count = counts[c][t] if t in counts[c] else 0
                count_sum += float(count)
                row.append(count)
            row.append(count_sum)
            writer.writerow(row)

if __name__ == "__main__":
    main()

