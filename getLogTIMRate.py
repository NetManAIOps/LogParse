#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# Get LogTIM rate of all algorithms.

import os
import csv

basePath = "./"
tailRawlogPath = basePath+"data/"
headTemplatePath = basePath+"results/"
tailTemplatePath = basePath+"results/logTIM_results/"
algorithmPath = os.listdir(tailTemplatePath)
tempPath = os.listdir(tailTemplatePath+algorithmPath[0])
datasetPath = [x for x in tempPath if "0.1" in x]
result = []

for algorithm in algorithmPath:
    for dataset in datasetPath:
        temp = dataset.split("_")
        tempTailDataset = temp[0]+"_tail_"+temp[1]
        tempHeadDataset = temp[0]+"_head_"+temp[1]
        tempData = [algorithm,dataset,headTemplatePath+algorithm+"/"+tempHeadDataset,tailTemplatePath+algorithm+"/"+dataset,tailRawlogPath+tempTailDataset+"/rawlog.log"]
        try:
            with open(tempData[2]+"/logTemplates.txt","r") as headFile:
                with open(tempData[3]+"/logTemplates.txt","r") as tailFile:
                    headTemplates = headFile.readlines()
                    tailTemplates = tailFile.readlines()
                    headNum = len(headTemplates)
                    tailNum = len(tailTemplates)
            # logIndex = []
            # tempResult = []
            # for i in range(headNum+1,tailNum+1):
            #     with open(tempData[3]+"/template"+str(i)+".txt","r") as tempTemplateFile:
            #         nowIndex = tempTemplateFile.readlines()
            #         logIndex.extend(nowIndex)
            # with open(tempData[4],"r") as rawlogFile:
            #     rawlog = rawlogFile.readlines()
            #     for index in logIndex:
            #         tempResult.append(rawlog[index])
            #     with open(tailRawlogPath+tempTailDataset+"/unMatchedLog.txt","w") as unMatchFile:
            #         unMatchFile.writelines(tempResult)
            #     # with open(tailRawlogPath+tempTailDataset+"/unMatchedIndex.txt","w") as indexFile:
            #     #     for i in tempResult:
            #     #         pass

            tempResult = []
            for i in range(headNum+1,tailNum+1):
                with open(tempData[3]+"/template"+str(i)+".txt","r") as tempTemplateFile:
                    nowlog = tempTemplateFile.readlines()
                    tempResult.extend(nowlog)
            unMatchedPath = tailRawlogPath+tempTailDataset+"/"+algorithm+"_unMatchedLog.txt"
            with open(unMatchedPath,"w") as unMatchFile:
                unMatchFile.writelines(tempResult)
            originSize = os.path.getsize(tempData[4])
            unMatchedSize = os.path.getsize(unMatchedPath)
            result.append([algorithm,dataset,originSize,unMatchedSize,round(unMatchedSize/originSize,5)])
        except:
            result.append([algorithm,dataset,"--","--","--"])


with open("result_unMatch.csv","w") as resultFile:
    csvFile = csv.writer(resultFile)
    csvFile.writerow(["algorithm","dataset","origin_size","unmatched_size","rate"])
    csvFile.writerows(result)
