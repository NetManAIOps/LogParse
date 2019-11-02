#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import argparse
import re

VALID_LINE_REGL = ['^\d+-\d+-\d+ .*']

if __name__ == "__main__":
#USAGE: ./logFilter.py [-input {INPUT_PATH}] [-output {OUTPUT_PATH}]
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', help = "input rawlog path", type = str, default = 'rawlog.log')
    parser.add_argument('-output', help = 'output rawlog path', type = str, default = 'rawlog.log.after')
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output

    rawlines = open(input_path, "r").readlines();
    outputlines = []
    invalid_lines = []
    invalid_num = 0
    for l in rawlines:
        valid = True
        for rex in VALID_LINE_REGL:
            if not re.match(rex, l):
                valid = False
                break
        if valid:
            outputlines.append(l.strip())
        else:
            invalid_num += 1
            # invalid_lines.append(l.strip())
            # print("invalid: %s"%l.strip())
        
    open(output_path, "w").write("\n".join(outputlines))
    print("invalid line num: %d"%invalid_num)
    # open("check.tmp", "w").write("\n".join(invalid_lines))
