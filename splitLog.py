#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from globalConfig import *
import os
import shutil
import argparse

def removecols(lines, dataset):
    '''remove the columns

    Args:
    --------
    lines: the list of data lines to be removed columns, with line format of [INDEX/TAB/RAWLOG]
    dataset: the name of dataset

    Returns:
    --------
    a list of data lines with columns removed, each line format of [INDEX/TAB/RAWLOG]
    '''
    index = [i.split("\t")[0] for i in lines]
    raw_lines = [i.split("\t")[1] for i in lines]
    to_remove = removeCol[dataset]
    clean_lines = [" ".join([i.split(" ")[k] for k in range(len(i.split(" "))) if k not in to_remove]) for i in raw_lines]
    return ["\t".join([index[k], clean_lines[k]]) for k in range(len(lines))]


if __name__ == "__main__":
# USAGE: ./splitLog.py [-dataset {DATASET}] [-ratio {RATIO}] [-reprocess {REPROCESS_FLAG}]
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', help = DATASET_STR, type = str, default = '2kBGL')
    parser.add_argument('-ratio', help = 'the ratio of the head data', type = float, default = 0.5)
    parser.add_argument('-reprocess', help = 'reprocess the _all data even if already exist', type = bool, default = False)
    args = parser.parse_args()
    target = args.dataset
    ratio = args.ratio
    reprocess = args.reprocess

    assert target in DATASET_LIST and ratio < 1 and ratio > 0
    data_dir = os.path.join(DATA_PATH, target)
    head_dir = os.path.join(DATA_PATH, "%s_head_%0.2f"%(target, ratio))
    tail_dir = os.path.join(DATA_PATH, "%s_tail_%0.2f"%(target, ratio))
    all_dir = os.path.join(DATA_PATH, "%s_all"%target)
    
    # clean the path to save results
    if os.path.exists(head_dir):
        shutil.rmtree(head_dir)
        os.makedirs(head_dir)
    else: os.makedirs(head_dir)
    if os.path.exists(tail_dir):
        shutil.rmtree(tail_dir)
        os.makedirs(tail_dir)
    else: os.makedirs(tail_dir)
    
    # process the rawlog file
    rawlines = open(os.path.join(data_dir, "rawlog.log"), "r", encoding="utf-8", errors="ignore").readlines()
    if len(rawlines[0].split("\t")) == 1:
        rawlines = ["\t".join([str(i+1), rawlines[i]]) for i in range(len(rawlines))]
    split_index = int(len(rawlines)*ratio)
    head_rawlines = removecols(rawlines[:split_index], target)
    tail_rawlines = removecols(["\t".join((str(int(k[0])-split_index), k[1])) for k in [i.split("\t") for i in rawlines[split_index:]]], target) # re-indexed
    open(os.path.join(head_dir, "rawlog.log"), "w").write("".join(head_rawlines))
    open(os.path.join(tail_dir, "rawlog.log"), "w").write("".join(tail_rawlines))

    # process the template files
    template_map = None
    if os.path.exists(os.path.join(data_dir, "groundtruth.seq")):
        template_map = open(os.path.join(data_dir, "groundtruth.seq"), "r").readlines()
        head_groundtruth = template_map[:split_index]
        tail_groundtruth = template_map[split_index:]

        template_change = {} # original template re-indexed
        for i in head_groundtruth:
            index, template = i.strip().split(" ")
            if template not in template_change.keys():
                template_change[template] = len(template_change)+1 
            with open(os.path.join(head_dir, "template%d.txt"%template_change[template]), "a") as f:
                f.write(index+"\n")

        template_change = {} # original template re-indexed
        for i in tail_groundtruth:
            index, template = i.strip().split(" ")
            if template not in template_change.keys():
                template_change[template] = len(template_change)+1
            with open(os.path.join(tail_dir, "template%d.txt"%template_change[template]), "a") as f:
                f.write(str(int(index)-split_index)+"\n")
    
    # process _all data if needed
    if reprocess or (not os.path.exists(all_dir)):
        if os.path.exists(all_dir):
            shutil.rmtree(all_dir)
            os.makedirs(all_dir)
        else: os.makedirs(all_dir)
        all_rawlines = removecols(rawlines, target)
        open(os.path.join(all_dir, "rawlog.log"), "w").write("".join(all_rawlines))
        if template_map:
            for i in template_map:
                index, template = i.strip().split(" ")
                with open(os.path.join(all_dir, "template%s.txt"%template), "a") as f:
                    f.write(index+"\n")
