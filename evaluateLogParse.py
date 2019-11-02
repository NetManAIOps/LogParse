#!/usr/bin/env python
#coding=utf-8
import sys
from globalConfig import *
sys.path.append(ALGORITHM_PATH)

import IPLoM as iplom
import LogSig as logsig
import LKE.LKE as lke
import Spell as spell
import Drain as drain
import MoLFI.MoLFI as molfi
### use subprocess to run ft_tree instead
# sys.path.append('ft_tree/')
# import ft_tree
# from matchTemplate import *

from RI_precision import *
from globalConfig import *
from numpy import *
import numpy as np
import time
import os
import shutil
import argparse
import subprocess

def createDir(path, removeflag=0):
    if removeflag == 1:
        shutil.rmtree(path)
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

def evaluateMethods(dataset, algorithm, leaf_num = 30, logname='rawlog.log', choose='all', ratio=0.5, eval_flag=1):
    if choose == 'all':
        dataPath = os.path.join(DATA_PATH, '%s_all/'%dataset)
        dataName = '%s_all'%dataset
    else:
        dataPath = os.path.join(DATA_PATH, '%s_%s_%0.2f/'%(dataset,choose,ratio))
        dataName = '%s_%s_%0.2f'%(dataset,choose,ratio)
    groupNum = int(GroupNum[dataset][choose]*0.5) # caution!
    removeCol=[] # caution!
    result = np.zeros((1,9))

    #####LogSig##############
    if algorithm == "LogSig":
        print('dataset:',logname)
        t1=time.time()
        parserPara = logsig.Para(path=dataPath, logname=logname, groupNum=groupNum, removeCol=removeCol, rex=regL[dataset], savePath=RESULT_PATH+algorithm+'_results/'+dataName+'/')
        myParser = logsig.LogSig(parserPara)
        runningTime = myParser.mainProcess()
        t2=time.time()
        # print 'cur_result_path:','./results/LogSig_results/' + dataName+'/'
        # createDir('./results/LogSig_results/' + dataName+'/' + dataName,1)
        if eval_flag:
            parameters = prePara(groundTruthDataPath=dataPath, logName=logname, geneDataPath=RESULT_PATH+algorithm+'_results/'+dataName+'/')
            TP,FP,TN,FN,p,r,f,RI = process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #####Spell################
    if algorithm == "Spell":
        print('dataset:', logname)
        t1=time.time()
        parser = spell.LogParser(indir=dataPath, outdir=RESULT_PATH+algorithm+'_results/'+dataName+'/', log_format='<Content>', tau=0.5, rex=regL[dataset])
        parser.parse(logname)
        t2=time.time()

        if eval_flag:
            parameters=prePara(groundTruthDataPath=dataPath ,logName = logname , geneDataPath=RESULT_PATH+algorithm+'_results/' + dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #####Drain################
    if algorithm == "Drain":
        print('dataset:', logname)
        t1=time.time()
        parser = drain.LogParser(indir=dataPath, outdir=RESULT_PATH+algorithm+'_results/'+dataName+'/', log_format='<Content>', st=0.5, depth=4, rex=regL[dataset])
        parser.parse(logname)
        t2=time.time()

        if eval_flag:
            parameters=prePara(groundTruthDataPath=dataPath ,logName = logname , geneDataPath=RESULT_PATH+algorithm+'_results/' + dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #####MoLFI################
    if algorithm == "MoLFI":
        print('dataset:', logname)
        t1=time.time()
        parser = molfi.LogParser(indir=dataPath, outdir=RESULT_PATH+algorithm+'_results/'+dataName+'/', log_format='<Content>', rex=regL[dataset])
        parser.parse(logname)
        t2=time.time()

        if eval_flag:
            parameters=prePara(groundTruthDataPath=dataPath ,logName = logname , geneDataPath=RESULT_PATH+algorithm+'_results/' + dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #####FT_tree##############
    if algorithm == "FT_tree":
        #training
        t1=time.time()
        log_path = dataPath+logname
        createDir(RESULT_PATH+"FT_tree_results/"+dataName+'/',0)
        template_path = RESULT_PATH+"FT_tree_results/"+dataName+'/' # + "logTemplate.txt"
        ## leaf_num = 5
        #ft_tree.getLogsAndSave(log_path, template_path + "/logTemplate.txt" , leaf_num)
        ##matching
        #matchTemplatesAndSave(log_path,template_path)
        out_seq_path = os.path.join(template_path, "matchTemplates.seq")
        templates = os.path.join(template_path, "logTemplates.txt")
        fre_word_path = os.path.join(template_path, "output.fre")
        middle_templates = os.path.join(template_path, "output.template_middle")
        sub_args = [
            os.path.join(ALGORITHM_PATH, "./ft_tree/main_train.py"),
            "-train_log_path", log_path,
            "-out_seq_path", out_seq_path,
            "-templates", templates,
            "-fre_word_path", fre_word_path,
            "-middle_templates", middle_templates,
            "-short_threshold", "1",
        ]
        subprocess.run(sub_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t2=time.time()

        # fix the format 
        for i in glob(os.path.join(template_path, "template[0-9]*.txt")):
            os.remove(i)
        match_lines = open(out_seq_path, "r").readlines()
        for i in range(len(match_lines)):
            template_index_str = match_lines[i].strip()
            assert int(template_index_str) > 0, "%d: %s"%(i, template_index_str)
            template_file = os.path.join(template_path, "template%s.txt"%template_index_str)
            with open(template_file, "a") as f:
                f.write(str(i+1)+"\n")

        #evaluation
        if eval_flag:
            parameters = prePara(groundTruthDataPath=dataPath, logName=logname, geneDataPath=RESULT_PATH+"FT_tree_results/"+dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')

        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #######LKE##############
    if algorithm == "LKE":
        print ('dataset:',logname, "LKE")
        t1=time.time()

        # parserPara = lke.Para(path=dataPath, dataName='', logname = logname,  removeCol=removeCol, rex=regL, savePath='./results/'+algorithm+'_results/' + dataName+'/')
        # print ('parserPara.path',parserPara.path)
        # myParser = lke.LKE(parserPara)
        # runningTime = myParser.mainProcess()
        parser = lke.LogParser(log_format='<Content>', indir=dataPath, outdir=RESULT_PATH+algorithm+'_results/'+dataName+'/', rex=regL[dataset], split_threshold=3)
        parser.parse(logname)
        t2=time.time()
        # print 'cur_result_path:','./results/LogSig_results/' + dataName+'/'
        #createDir('./results/LKE_results/' + dataName+'/' + dataName,1)
        if eval_flag:
            parameters=prePara(groundTruthDataPath=dataPath ,logName = logname , geneDataPath=RESULT_PATH+algorithm+'_results/' + dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

    #######IPLoM############
    if algorithm == "IPLoM":
        print ('dataset:',logname, "IPLoM")
        t1=time.time()
        parserPara = iplom.Para(path=dataPath,  logname = logname,removeCol=removeCol, rex=regL[dataset], savePath=RESULT_PATH+algorithm+'_results/' + dataName+'/')
        print ('parserPara.path',parserPara.path)
        myParser = iplom.IPLoM(parserPara)
        runningTime = myParser.mainProcess()
        t2=time.time()
        # print 'cur_result_path:','./results/LogSig_results/' + dataName+'/'
        #createDir('./results/LKE_results/' + dataName+'/' + dataName,1)
        if eval_flag:
            parameters=prePara(groundTruthDataPath=dataPath ,logName = logname , geneDataPath=RESULT_PATH+algorithm +'_results/' + dataName+'/')
            TP,FP,TN,FN,p,r,f,RI=process(parameters)
        else: print('No evaluation')
        print ('dataset:', logname)
        print ('training time: %0.3f'%(t2-t1))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', help = DATASET_STR, type = str, default = '2kBGL')
    parser.add_argument('-algorithm', help = ALGORITHM_STR, type = str, default = 'LKE')
    parser.add_argument('-choose', help = 'head, tail, all', type = str, default = 'head')
    parser.add_argument('-ratio', help = 'the ratio of the head data', type = float, default = '0.5')
    parser.add_argument('-eval', help = 'flag to evaluate', type = int, default = 1)
    # parser.add_argument('-leaf_num', help = 'for ft-tree', type = int, default = 30)
    args = parser.parse_args()
    dataset = args.dataset
    algorithm = args.algorithm
    assert dataset in DATASET_LIST
    assert algorithm in ALGORITHM_LIST
    # leaf_num = args.leaf_num #对于ft-tree会用到
    evaluateMethods(dataset, algorithm, choose=args.choose, ratio=args.ratio, eval_flag=args.eval)
    print ('algorithm:',algorithm)
    print ('Dataset',dataset)
