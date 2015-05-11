#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
import natsort
import os
import pprint
from re import sub
from sys import argv, exit
import csv

FILE_EXTENSION = '.raw'

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
    if len(argv) != 2:
        print "Usage: %s <file>" % argv[0]
        exit(0)

    log_file = argv[1]

    if not os.path.exists(log_file) or not log_file.endswith(FILE_EXTENSION):
        print "## '%s' is not a valid file" % log_file
        exit(0)

    # Array to store tag combinations
    combination = sub(FILE_EXTENSION, '', log_file.split('/')[-1])
    counts = {}
    abst_tags = {}

    with open(log_file) as f:
        for l in f.readlines():
            if l.startswith('#') or l.startswith('PCBits'):
                continue

            # should containts = count, rssi, tag, pcbits
            pcbits, rssi, tag, user_memory = l.split()
            pc = PCBits(int(pcbits, 10))
            if pc.nsi == 0 and pc.epc_length == 96: # GS1
                if not tag.startswith('302DB'):
                    standard = "PROPRIETARY"
                else:
                    standard = "GS1"
            elif pc.nsi == 1 and 0xA1 <= pc.afi <= 0xAA: # ISO
                standard = get_iso_from_afi(pc.afi)
            else:
                standard = "PROPRIETARY"

            # name tag
            tag_type = None
            if tag in abst_tags.values():
                for k, v in abst_tags.iteritems():
                    if tag == v:
                        tag_type = k
            else:
                for i in range(1000):
                    tag_type = standard + '_' + str(i)
                    if tag_type not in abst_tags.keys():
                        abst_tags[tag_type] = tag
                        break
            if tag_type not in counts:
                counts[tag_type] = 0 
            counts[tag_type] += 1

    tags = natsort.natsorted(counts.keys(), key=lambda t: counts[t])
    pp = pprint.PrettyPrinter(indent = 2)
    pp.pprint(abst_tags)
    pp.pprint(counts)

    with open(combination + '_count.csv', 'wb') as f:
        writer = csv.writer(f)
        head = ['Tag']
        types = list(set([sub('_[0-9]+', '', t) for t in tags]))
        types.sort()
        print types
        head += types
        writer.writerow(head)
        for t in tags:
            tag_type = sub('_[0-9]+', '', t)
            row = [abst_tags[t]]
            for tt in types:
                if tag_type == tt:
                    row.append(counts[t]/3)
                else:
                    row.append(0)
            writer.writerow(row)

if __name__ == "__main__":
    main()

