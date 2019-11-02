#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from RI_precision import *
from globalConfig import *
import os
from glob import glob
import sys
import shutil

def retrain_evaluate(gtData_path, geneData_path, ratio):
    '''evaluate the retrain results

    Args:
    --------
    gtData_path: groundtruth data directory, i.e. _tail dataset path
    geneData_path: generate data directory, i.e. _all results path
    ratio: the split ratio of _head data

    Returns:
    --------
    None
    '''
    # create temporary directory to save the _tail data from _all
    tmp_dir = os.path.join(geneData_path, "tmp_dir")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # split the geneData
    fileNum = len(glob(os.path.join(geneData_path, "template[0-9]*.txt")))
    all_line_num = 0
    for i in range(fileNum):
        all_line_num += len(open(os.path.join(geneData_path, "template%s.txt"%(i+1)), "r").readlines())
    split_index = int(all_line_num*ratio)
    for i in range(fileNum):
        filename = os.path.join(geneData_path, "template%s.txt"%(i+1))
        tmp_file = os.path.join(tmp_dir, "template%s.txt"%(i+1))
        filtered = [str(int(k.strip().split("\t")[0])-split_index) for k in open(filename , "r").readlines() if int(k.strip().split("\t")[0])>split_index]
        open(tmp_file, "w").write("\n".join(filtered))

    parameters = prePara(groundTruthDataPath=gtData_path+'/', geneDataPath=tmp_dir+'/')
    TP, FP, TN, FN, p, r, f, RI = process(parameters)

    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
# USAGE: ./retrain.py {ALGORITHM} {DATASET} {RATIO}
    printLine()
    assert sys.argv[1] in ALGORITHM_LIST
    assert sys.argv[2] in DATASET_LIST

    config = {
        "algorithm":sys.argv[1],
        "dataset":sys.argv[2],
        "ratio":float(sys.argv[3])
    }

    gene_data_path = os.path.abspath(os.path.join(RESULT_PATH, "%s_results"%config["algorithm"], "%s_all"%config["dataset"]))
    groundtruth_path = os.path.abspath(os.path.join(DATA_PATH, "%s_tail_%0.2f"%(config["dataset"], config["ratio"])))

    retrain_evaluate(groundtruth_path, gene_data_path, config["ratio"])
