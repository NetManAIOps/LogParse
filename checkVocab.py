#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from globalConfig import *
import os
import argparse
from logTIM import regL
from matchTree import MatchTree
import re


def matchTemplate(log, matcher):
    '''match log with template

    Args:
    --------
    log: clean rawlog line
    matcher: MatchTree object

    Returns:
    --------
    template index and variables string if match successfully, otherwise None
    '''
    log_words = log.strip().split(" ")
    return matcher.match_template(log_words)

def checkVocab(logTemplatePath, rawLogPath, dataSet, saveDir=""):
    '''match and find the template-as-well-as-variables vocab in rawlog

    Args:
    --------
    logTemplatePath: the path to logTemplate file, i.e. logTemplates.txt
    rawLogPath: the path to rawlog file, i.e. rawlog.log
    dataSet: the name of the dataset, used to clean log
    saveDir: the path to save directory, default ""

    Returns:
    --------
    intersect_vocab: the set of template-as-well-as-variables vocab
    template_vocab: the set of template vocab
    variable_vocab: the set of variable vocab
    '''
    print("checkVocab...")
    print("logTemplatePath: %s" % logTemplatePath)
    print("rawLogPath: %s" % rawLogPath)

    def cleanLog(log, rex):
        for currentRex in rex:
            log = re.sub(currentRex, "", log)
        return log

    def getRaw(line):
        # remove the might-exist index
        parts = line.split("\t")
        assert len(parts) <= 2
        if len(parts) == 2:
            return cleanLog(parts[1].strip(), regL[dataSet])
        else:
            return cleanLog(line.strip(), regL[dataSet])

    template_lines = [getRaw(i) for i in open(logTemplatePath, "r").readlines()]
    template_vocab = set()
    for line in template_lines:
        vocab = line.split(" ")
        template_vocab = template_vocab.union(vocab)
    if "*" in template_vocab:
        template_vocab.remove("*")

    template_map = dict(zip([i+1 for i in range(len(template_lines))], [i.split(" ") for i in template_lines]))
    matcher = MatchTree()
    for t_id, t_list in template_map.items():
        matcher.add_template(t_list, template_id=t_id)

    rawlog_lines = [getRaw(i) for i in open(rawLogPath, "r").readlines()]
    variable_vocab = set()
    unmatch_lines = [] 
    for i in range(len(rawlog_lines)): 
        line = rawlog_lines[i] 
        match_result = matchTemplate(line, matcher)
        # assert index, line
        if not match_result: 
            unmatch_lines.append("\t".join([str(i+1), line])) 
            continue 
        variable_vocab = variable_vocab.union(match_result[1].split(" "))
    if unmatch_lines: 
        # uncomment the following line to save unmatched_lines and check mannually
        # open("unmatch_lines_%s.debug"%dataSet, "w").write("\n".join(unmatch_lines)+'\n') 
        print("unmatch_lines: %d"%len(unmatch_lines))
    intersect_vocab = template_vocab.intersection(variable_vocab)
    print("number of template-as-well-as-variable vocab is %d" % len(intersect_vocab))
    print("rate of template-as-well-as-variable vocab is %f" % (len(intersect_vocab)/len(variable_vocab.union(template_vocab))))
    if saveDir:
        print("save to %s" % saveDir)
        if not os.path.exists(saveDir):
            os.path.makedirs(saveDir)
        open(os.path.join(saveDir, "intersect_vocab.txt"), "w").write("\n".join(list(intersect_vocab)))
        open(os.path.join(saveDir, "template_vocab.txt"), "w").write("\n".join(list(template_vocab)))
        open(os.path.join(saveDir, "variable_vocab.txt"), "w").write("\n".join(list(variable_vocab)))

    return intersect_vocab, template_vocab, variable_vocab


if __name__ == "__main__":
# USAGE: ./checkVocab.py [-dataset {DATASET}] [-algorithm {ALGORITHM}] [-save {SAVEPATH}] [-ratio {RATIO}]
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', help = DATASET_STR, type = str, default = '2kBGL')
    parser.add_argument('-algorithm', help = ALGORITHM_STR, type = str, default = 'IPLoM')
    parser.add_argument('-save', help = 'directory to save file', type = str, default = '')
    parser.add_argument('-ratio', help = 'ratio of the head data', type = float, default = 0.5)
    args = parser.parse_args()
    assert args.dataset in DATASET_LIST and args.algorithm in ALGORITHM_LIST

    logTemplatePath = os.path.join(RESULT_PATH, "logTIM_results/%s_results/%s_%0.2f/logTemplates.txt"%(args.algorithm, args.dataset, args.ratio))
    # rawLogPath = "./data/%s_all/rawlog.log"%args.dataset
    rawLogPath = os.path.join(DATA_PATH, "%s_head_%0.2f/rawlog.log"%(args.dataset, args.ratio))
    checkVocab(logTemplatePath, rawLogPath, args.dataset, args.save)
