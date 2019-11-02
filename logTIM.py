#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from globalConfig import *
from classifier import *
from RI_precision import *
from getVocab import createDir, get_word_context
from compressRate import compressRate
from matchTree import MatchTree
import re
import sys
import time

# incremental file reader (used in depolyment)
class FileReader:
    def __init__(self, filePath):
        self.filePath = filePath
        self.readed = 0
        with open(filePath, "r") as f:
            self.label = f.tell()
    
    def reset(self):
        with open(self.filePath, "r") as f:
            self.label = f.tell()
        self.readed = 0

    def readIncr(self):
        fd = open(self.filePath, "r")
        fd.seek(self.label, 0)
        increment = fd.readlines()
        self.label = fd.tell()
        fd.close()
        if increment:
            print("read %d lines from %s" % (len(increment), self.filePath))
        startfrom = self.readed
        self.readed += len(increment)
        return increment, startfrom


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


def newTemplate(log, clf, contextNum):
    '''give new template by classifier

    Args:
    --------
    log: clean rawlog line
    clf: classifier
    context_num: list of the number of words to choose in the context, [preceding, succeeding]

    Returns:
    --------
    new_template: a list of new template words
    '''
    words = log.strip().split(" ")
    vector_list = []
    for i in range(len(words)):
       vector_list.append(get_feature_vec(get_word_context(words, i, contextNum)))

    prediction = list(clf.predict(np.array(vector_list)))
    assert len(prediction) == len(words)
    
    def replaceVar(index):
        if prediction[index] == -1.0:
            return "*"
        elif prediction[index] == 1.0:
            return words[index]
        else: return "?"

    new_template = [replaceVar(i) for i in range(len(prediction))]
    return new_template


def logtim(trainData_path, logFile_path, rawLog_path, geneData_path, gtData_path, rex=[], realtime=False, contextNum=[1,0], eval_flag=1):
    '''logtim process: train classifier from _head results, then use _tail data to match and increment

    Args:
    --------
    trainData_path: the path to training data for classifier
    logFile_path: the path to _tail rawlog
    rawLog_path: the path to _head data directory
    geneData_path: the directory path to save generated results
    gtData_path: the path to groundtruth data directory
    rex: list of regular rules to clean the rawlog, default []
    realtime: set real time process or not, default False, only set True when real deployment
    contextNum: list of the number of vocabulary to choose in the context, [preceding, succeeding], default [1,0]
    eval_flag: flag to decide whether to evaluate the results, default 1

    Returns:
    --------
    None
    '''
    print("logTIM processing")
    print("trainData_path: %s" % trainData_path)
    print("logFile_path: %s" % logFile_path)
    print("rawLog_path: %s" % rawLog_path)
    print("geneData_path: %s" % geneData_path)
    print("gtData_path: %s" % gtData_path)
    print("rex:", rex)
    print("realtime:", realtime)
    print("contextNum:", contextNum)
    print("eval_flag:", eval_flag)
    printLine()

    t1 = time.time()
    createDir(geneData_path, removeflag=1)

    # get matcher and template_map dictionary (key=index, value=template_word_list)
    templates_path = os.path.join(trainData_path, "logTemplates.txt")
    if config["algorithm"] == "IPLoM":
        # IPLoM's logTemplates.txt has index at the start of each line
        template_map = dict([line.strip().split("\t") for line in open(templates_path, "r").readlines()])
    else:
        lines = [i.strip() for i in open(templates_path, "r").readlines()]
        index = [i+1 for i in range(len(lines))]
        template_map = dict(zip(index, lines))
    for key in template_map.keys():
        template_map[key] = template_map[key].strip().split(" ")
    matcher = MatchTree()
    for t_id, t_list in template_map.items():
        matcher.add_template(t_list, template_id=t_id)
    original_template_num = matcher.templateNum()
    del template_map
    print("Original template num: %d" %original_template_num)

    # SVM classifier
    train_data, train_labels, _, _ = data_loader(trainData_path, trainingRate=1, rawlogPath=rawLog_path, rex=rex, contextNum=contextNum)
    clf = SVM(train_data, train_labels, _, _, test=False)
    del train_data, train_labels, _
    t2 = time.time()

    # match and increment
    logReader = FileReader(logFile_path)
    match_results = []
    printLine()
    if not realtime:
        rawlogs, line_index = logReader.readIncr()
        if len(rawlogs[0].strip().split("\t")) == 1:
            # formulate the format
            rawlogs = ["\t".join([str(k+1+line_index), rawlogs[k]]) for k in range(len(rawlogs))]
        for log in rawlogs:
            log_index, log_raw = log.strip().split("\t")
            for currentRex in rex:
                log_raw = re.sub(currentRex, "", log_raw)
            match_result = matchTemplate(log_raw, matcher)
            if match_result:
                match_results.append(match_result)
            else:
                matcher.add_template(newTemplate(log_raw, clf, contextNum))
                match_result = matchTemplate(log_raw, matcher)
                assert match_result, log_raw
                match_results.append(match_result)
                # print("New template %d from log: %s" % (template_num, log.strip()))
                # print("Template: %s" % template_map[str(template_num)])

            gene_path = os.path.join(geneData_path, "template%d.txt"%match_results[-1][0])
            with open(gene_path, "a") as f:
                f.write(log)
        t3 = time.time()
        template_map = matcher.template_map
        for key in template_map.keys():
            template_map[key] = " ".join(template_map[key])
            if not os.path.exists(os.path.join(geneData_path, "template%d.txt"%key)):
                with open(os.path.join(geneData_path, "template%d.txt"%key), "w") as f:
                    f.write("")
        
        template_map_sorted = sorted(template_map.items(), key=lambda x:x[0])
        open(os.path.join(geneData_path, "logTemplates.txt"), "w").write("\n".join(["\t".join(map(str, i)) for i in template_map_sorted]))
        open(os.path.join(geneData_path, "matchResults.txt"), "w").write("\n".join(["\t".join(map(str, i)) for i in match_results]))
        print("final template num: %d" %matcher.templateNum())
        print("new template num: %d" %(matcher.templateNum()-original_template_num))
        print("training time: %0.3f"%(t2-t1))
        print("match time: %0.3f"%(t3-t2))
        print("whole time: %0.3f"%(t3-t1))
        
        if eval_flag:
            if eval_flag == 1: print("internal evaluation")
            if eval_flag == 2: print("cross evaluation")
            parameters = prePara(groundTruthDataPath=gtData_path+'/', geneDataPath=geneData_path+'/')
            TP, FP, TN, FN, p, r, f, RI = process(parameters)
        else: print("No evaluation")

        print("compress rate is %0.2f"%compressRate(geneData_path, logFile_path))
    else:
        # TODO: real deployment
        pass

if __name__ == "__main__":
# USAGE: ./logTIM.py {ALGORITHM} {DATASET} {RATIO} {EVAL_FLAG}
    assert sys.argv[1] in ALGORITHM_LIST
    assert sys.argv[2] in DATASET_LIST
    assert sys.argv[4] in ['0', '1', '2']

    config = {
        "algorithm":sys.argv[1],
        "dataset":sys.argv[2],
        "ratio":sys.argv[3],
        "eval":int(sys.argv[4]),
    }

    if config["eval"] == 2:
    # cross evaluation
        train_data_path = os.path.abspath(os.path.join(RESULT_PATH, "%s_results"%config["algorithm"], "%s_all"%config["dataset"]))
        log_data_path = os.path.abspath(os.path.join(DATA_PATH, "%s_all"%config["ratio"], "rawlog.log")) # target dataset name in "ratio" when cross evaluation
        raw_log_path = os.path.abspath(os.path.join(DATA_PATH, "%s_all"%config["dataset"]))
        gene_data_path = os.path.abspath(os.path.join(RESULT_PATH, "logTIM_results", "%s_results"%config["algorithm"], "%s_TO_%s"%(config["dataset"], config["ratio"])))
        groundtruth_path = os.path.abspath(os.path.join(DATA_PATH, "%s_all"%config["ratio"]))
    else:
    # no evaluation or internal evaluation
        config["ratio"] = float(config["ratio"])
        train_data_path = os.path.abspath(os.path.join(RESULT_PATH, "%s_results"%config["algorithm"], "%s_head_%0.2f"%(config["dataset"], config["ratio"])))
        log_data_path = os.path.abspath(os.path.join(DATA_PATH, "%s_tail_%0.2f"%(config["dataset"], config["ratio"]), "rawlog.log"))
        raw_log_path = os.path.abspath(os.path.join(DATA_PATH, "%s_head_%0.2f"%(config["dataset"], config["ratio"])))
        gene_data_path = os.path.abspath(os.path.join(RESULT_PATH, "logTIM_results", "%s_results"%config["algorithm"], "%s_%0.2f"%(config["dataset"], config["ratio"])))
        groundtruth_path = os.path.abspath(os.path.join(DATA_PATH, "%s_tail_%0.2f"%(config["dataset"], config["ratio"])))

    logtim(train_data_path, log_data_path,raw_log_path, gene_data_path, groundtruth_path, rex=regL[config["dataset"]], contextNum=[ContextNum["preceding_word_num"],ContextNum["succeeding_word_num"]], eval_flag=config["eval"])
