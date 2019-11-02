#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys
import random
import shutil
import re
from glob import glob

def createDir(path, removeflag=0):
    if os.path.exists(path):
        if removeflag == 1:
            shutil.rmtree(path)
            os.makedirs(path)
    else: os.makedirs(path)
        
def cleanLog(log, rex):
    for currentRex in rex:
        log = re.sub(currentRex, "", log)
    return log

def get_word_context(word_list, word_index, context_num):
    '''get the context of a word from the word list of a log

    Args:
    --------
    word_list: a list of words in the log
    word_index: the target word's index in the list
    context_num: list of the number of words to choose in the context, [preceding, succeeding]

    Returns:
    --------
    word_context: a tuple of word context, with the first one to be the target word itself
    '''
    target_word = word_list[word_index]
    word_context = [target_word]
    for i in range(word_index-context_num[0], word_index+context_num[1]+1):
        if not i == word_index:
            if i>=0 and i<len(word_list):
                word_context.append(word_list[i])
            else:
                word_context.append("")
    return tuple(word_context)

def getVocab(inputPath, outputPath="", rawlogPath="", rex=[], contextNum=[1,0]):
    '''get template vocab and variable vocab for each template

    Args:
    --------
    inputPath: the path to input data directory
    outputPath: the path to save results if given, default ""
    rawlogPath: the path to rawlog file (maybe not in inputPath), default ""
    rex: list of regular rules to clean rawlog, default []
    contextNum: list of the number of vocabulary to choose in the context, [preceding, succeeding], default [1,0]

    Returns:
    --------
    template_vocab: dictionary (key=template_index, value={"template_vocab":set(), "variable_vocab":set()})
    '''
    # use logTemplates.txt and rawlog.log to get vocab
    rawlogsPath = os.path.join(rawlogPath, "rawlog.log")
    rawlogs = [cleanLog(i.strip(), rex) for i in open(rawlogsPath, "r").readlines()]
    if len(rawlogs[0].split("\t")) == 2:
        # if there is index at the start of each line
        rawlogs = [i.split("\t")[1].split(" ") for i in rawlogs]
    else:
        rawlogs = [i.split(" ") for i in rawlogs]

    logTemplatePath = os.path.join(inputPath, "logTemplates.txt")
    if not os.path.exists(logTemplatePath):
        # for groundtruth path specifically
        logTemplatePath = os.path.join(inputPath, "templates.txt")
        def fomatLine(line):
            line = " ".join([i.strip() for i in line.split(".*") if i.strip()])
            line = line.replace("\\", "")
            return line
        templates = [fomatLine(i) for i in open(logTemplatePath, "r").readlines()]
    else:
        templates = [i.strip() for i in open(logTemplatePath, "r").readlines()]
    if len(templates[0].split("\t")) == 2:
        # if there is index at the start of each line
        templates = [i.split("\t")[1].split(" ") for i in templates]
    else:
        templates = [i.split(" ") for i in templates]
    template_num = len(templates)
    template_vocab = {}
    for i in range(template_num):
        line_index = [int(k.strip().split("\t")[0])-1 for k in open(os.path.join(inputPath, "template%d.txt"%(i+1)), "r").readlines()]
        log_chosen = [rawlogs[k] for k in line_index]
        template_vocab[i+1] = {"template_vocab": set(), "variable_vocab": set()}
        for log in log_chosen:
            for j in range(len(log)):
                word_context = get_word_context(log, j, contextNum)
                if log[j] in templates[i]:
                    template_vocab[i+1]["template_vocab"].add(word_context)
                else:
                    template_vocab[i+1]["variable_vocab"].add(word_context)
    return template_vocab
            

if __name__ == "__main__":
# run __main__ function for debug
    input_dir = "../results/IPLoM_results/"
    output_dir = "./results/vocab/"
    data_set = "2kBGL"

    input_path = os.path.abspath(os.path.join(input_dir, data_set))
    output_path = os.path.abspath(os.path.join(output_dir, data_set))
    createDir(output_path, 1)
    print("input_path: %s\noutput_path: %s" % (input_path, output_path))

    getVocab(input_path, output_path)
