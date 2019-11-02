#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from globalConfig import *
from sklearn import svm
from sklearn import metrics
from getVocab import getVocab
import os
import numpy as np
import pandas as pd
import random
import argparse
import time

def get_feature_vec(word_context):
    '''get the feature vector of the word context 

    Args:
    --------
    word_context: a tuple of word context, with the first one to be the target word itself

    Returns:
    --------
    feature_vector: a list-like feature vector from word context, with the dimension of  WORD_NUM * 94
    '''
    # TODO: reduce the dimension
    # the dimension of a word vector is 94
    # a character's index is its ascii code minus 33
    # concat each word together to get feature vector
    feature_vec = []
    for word in word_context:
        word_vec = list([0.0 for i in range(94)])
        for char in list(word):
            word_vec[ord(char)-33] += 1.0 # (ascii - 33)
        feature_vec += word_vec
    return feature_vec

def data_loader(inputPath, trainingRate=0.5, rawlogPath="", rex=[], contextNum=[1,0]):
    '''load data for classifier training

    Args:
    --------
    inputPath: the path to input data directory
    trainingRate: the rate to split train data and testing data, default 0.5
    rawlogPath: the path to the rawlog file (maybe not in inputPath), default ""
    rex:list of regular rules to clean log, default []
    contextNum: list of the number of vocabulary to choose in the context, [preceding, succeeding], default [1,0]

    Returns:
    --------
    train_data: train data vector, each line for a word
    train_labels: train data labels, each line for a word label
    testing_data: testing data vector, each line for a word
    testing_labels: testing data labels, each line for a word label
    '''
    print("Data loaded from %s, trainning rate is %f" % (inputPath, trainingRate))
    template_vocab = getVocab(inputPath, rawlogPath=rawlogPath, rex=rex, contextNum=contextNum)

    vector_list = []
    for key, value in template_vocab.items(): 
        for plabel in value["template_vocab"]:
            vector_list.append((get_feature_vec(plabel), [1.0]))

        for nlabel in value["variable_vocab"]:
            vector_list.append((get_feature_vec(nlabel), [-1.0]))

    random.shuffle(vector_list)
    total_num = len(vector_list)
    divide_index = int(total_num*trainingRate)

    train_data = np.array([i[0] for i in vector_list[:divide_index]], dtype=float)
    train_labels = np.array([i[1] for i in vector_list[:divide_index]], dtype=float)
    testing_data = np.array([i[0] for i in vector_list[divide_index:]], dtype=float)
    testing_labels = np.array([i[1] for i in vector_list[divide_index:]], dtype=float)

    print("train_data shape is", train_data.shape)
    print("testing_data shape is", testing_data.shape)
    return train_data, train_labels, testing_data, testing_labels



def SVM(train_data, train_labels, testing_data, testing_labels, test=True):
    '''train SVM classifier

    Args:
    --------
    train_data: train data vector, each line for a word
    train_labels: train data labels, each line for a word label
    testing_data: testing data vector, each line for a word
    testing_labels: testing data labels, each line for a word label
    test: whether test or not, default True

    Returns:
    --------
    clf: SVM classifer
    '''
    print("SVM classifier")
    clf = svm.LinearSVC(penalty='l2', tol=1e-4, C=1.0, dual=True, fit_intercept=True, intercept_scaling=1, class_weight="balanced", max_iter=1000000)
    clf = clf.fit(train_data, train_labels.ravel())
    if not test:
        return clf

    prediction = list(clf.predict(testing_data))
    assert len(prediction) == len(testing_labels)
    printLine()
    print("accuracy: %0.3f"%metrics.accuracy_score(testing_labels, prediction))
    print("recall: %0.3f"%metrics.recall_score(testing_labels, prediction))
    print("f-score: %0.3f"%metrics.f1_score(testing_labels, prediction))
    printLine()
    return clf


if __name__ == "__main__":
# run __main__ function to evaluate classifier
# USAGE: ./classifier.py [-dataset {DATASET}] [-ratio {RATIO}] [-preceding {PRECEDING}] [-succeeding {SUCCEEDING}]
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', help = DATASET_STR, type = str, default = '2kBGL')
    parser.add_argument('-ratio', help = 'ratio to split training data', type = float, default = 0.5)
    parser.add_argument('-preceding', help = 'preceding word number', type = int, default = -1)
    parser.add_argument('-succeeding', help = 'succeeding word number', type = int, default = -1)
    args = parser.parse_args()
    dataset = args.dataset
    ratio = args.ratio
    if args.preceding < 0 or args.succeeding < 0:
        preceding = ContextNum["preceding_word_num"]
        succeeding = ContextNum["succeeding_word_num"]
    else:
        preceding = args.preceding
        succeeding = args.succeeding

    input_path = os.path.join(DATA_PATH, dataset)
    t1 = time.time()
    train_data, train_labels, testing_data, testing_labels = data_loader(input_path, trainingRate=ratio, rawlogPath=input_path, rex=regL[dataset], contextNum=[preceding, succeeding])
    SVM(train_data, train_labels, testing_data, testing_labels, test=True)
    t2 = time.time()
    print("time: %0.3f"%(t2-t1))
