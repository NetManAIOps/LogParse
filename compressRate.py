#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys
import argparse

def compressRate(compress_file_dir, raw_file_path): 
    '''calculate compress rate

    Args:
    --------
    compress_file_dir: the path to the reuslt directory of logtim
    raw_file_path: the path to the rawlog file

    Returns:
    --------
    compress rate
    '''
    # f1 = os.path.join(compress_file_dir, "matchResults.txt")
    # f2 = os.path.join(compress_file_dir, "logTemplates.txt")
    # compress_size = os.path.getsize(f1) + os.path.getsize(f2)
    f = os.path.join(compress_file_dir, "matchResults.txt")
    compress_size = os.path.getsize(f)
    raw_size = os.path.getsize(raw_file_path)
    return compress_size/raw_size

if __name__ == "__main__":
# run __main__ for debug
    parser = argparse.ArgumentParser()
    parser.add_argument('-compress', help = 'compress file directory', type = str, default = '')
    parser.add_argument('-raw', help = 'raw file path', type = str, default = '')
    args = parser.parse_args()
    print(compressRate(args.compress, args.raw))
