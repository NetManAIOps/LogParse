#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# Get decompress time of all dataset: press "1" for our algorithm, "2" for traditional algorithm and "3" for both.

import os
import time
import csv
import lzma
import gzip
import bz2

def compress_lzma(sourceFile,destFile):
    with lzma.open(destFile, 'wb') as des:
        with open(sourceFile, 'rb') as sou:
            des.write(sou.read())

def uncompress_lzma(sourceFile,destFile):
    with open(destFile, 'wb') as des:
        with lzma.open(sourceFile, 'rb') as sou:
            des.write(sou.read())

def compress_gzip(sourceFile,destFile):
    with gzip.open(destFile, 'wb') as des:
        with open(sourceFile, 'rb') as sou:
            des.write(sou.read())

def uncompress_gzip(sourceFile,destFile):
    with open(destFile, 'wb') as des:
        with gzip.open(sourceFile, 'rb') as sou:
            des.write(sou.read())

def compress_bzip2(sourceFile,destFile):
    with bz2.BZ2File(destFile, 'wb') as des:
        with open(sourceFile, 'rb') as sou:
            des.writelines(sou)

def uncompress_bzip2(sourceFile,destFile):
    with open(destFile, 'wb') as des:
        with bz2.BZ2File(sourceFile, 'rb') as sou:
            des.writelines(sou)

def compress_7zip(sourceFile,destFile):
    os.system("7z a -t7z {destfile} {sourcefile}".format(destfile=destFile,sourcefile=sourceFile))

def compress_zip(sourceFile,destFile):
    os.system("7z a -tzip {destfile} {sourcefile}".format(destfile=destFile,sourcefile=sourceFile))

def uncompress_7z(sourceFile):
    os.system("7z x {sourcefile} -y".format(sourcefile=sourceFile))

if __name__ == "__main__":
    print("Press key to get decompress time of all datasets:\n1 : Our algorithms.\n2 : Traditional algorithms.\n3 : Both Our algorithms and traditional algorithms.\n")    
    choose = input("Press: ")

    if choose == "2" or choose == "3":
        basePath = "./"
        resultPath = basePath+"results/logTIM_results/FT_tree_results/"
        dataPath = basePath+"data/"
        tempPaths = os.listdir(dataPath)
        rawlogPaths = [x for x in tempPaths if "tail" in x]
        logTemplatesName = "logTemplates.txt"
        matchResultsName = "matchResults.txt"
        rawlogName = "rawlog.log"
        result = []
        for path in rawlogPaths:
            rawlogPath = dataPath+path+"/"+rawlogName
            temp = path.split("_tail")
            temp = temp[0]+temp[1]
            tempBasePath = resultPath+temp+"/"
            try:
                tempBasePath=dataPath+path+"/"
                # compress_lzma(tempBasePath+"rawlog.log",tempBasePath+"rawlog.lzma")
                # compress_gzip(tempBasePath+"rawlog.log",tempBasePath+"rawlog.gz")
                # compress_bzip2(tempBasePath+"rawlog.log",tempBasePath+"rawlog.bz2")
                # compress_7zip(tempBasePath+"rawlog.log",tempBasePath+"rawlog.7z")
                # compress_zip(tempBasePath+"rawlog.log",tempBasePath+"rawlog.zip")
                time2 = time.time()
                uncompress_lzma(tempBasePath+"rawlog.lzma",tempBasePath+"rawlog_lzma.log")
                time3 = time.time()
                uncompress_gzip(tempBasePath+"rawlog.gz",tempBasePath+"rawlog_gz.log")
                time4 = time.time()
                uncompress_bzip2(tempBasePath+"rawlog.bz2",tempBasePath+"rawlog_bz2.log")
                time5 = time.time()
                uncompress_7z(tempBasePath+"rawlog.7z")
                time6 = time.time()
                uncompress_7z(tempBasePath+"rawlog.zip")
                time7 = time.time()
            except:
                result.append([temp,"--","--","--","--","--"])
                continue
            result.append([temp,round(time3-time2,5),round(time4-time3,5),round(time5-time4,5),round(time6-time5,5),round(time7-time6,5)])
        with open("decompress_traditional_result.csv","w") as resultFile:
            file_csv = csv.writer(resultFile)
            title = ["dataset","lzma_time","gzip_time","bzip2_time","7zip_time","zip_time"]  
            file_csv.writerow(title)
            file_csv.writerows(result)

    if choose=="1" or choose =="3":
        basePath = "./"
        resultBasePath = basePath+"results/logTIM_results/"
        algorithmPath = os.listdir(resultBasePath)
        datasets = os.listdir(resultBasePath+algorithmPath[0]+"/")
        logTemplatesName = "logTemplates.txt"
        matchResultsName = "matchResults.txt"
        result = []
        for path in algorithmPath:
            for dataset in datasets:
                try:
                    with open(resultBasePath+path+"/"+dataset+"/"+logTemplatesName,"r") as logFile: 
                        logTemplates = logFile.readlines()
                    with open(resultBasePath+path+"/"+dataset+"/"+matchResultsName,"r") as matchFile:
                        tempMatchResults = matchFile.readlines()
                    matchResults = []
                    ourResults = []

                    oneTime0 = time.time()
                    oneLogTemplates = [x[x.find("\t")+1:].split("*") for x in logTemplates]
                    # matchResults = []
                    one = tempMatchResults[0]
                    if one!="" and one[-1]=="\n":
                        one = one[:-1]
                    piece = [one[:one.find("\t")],one[one.find("\t")+1:].split(" ")]

                    oneResult = []   
                    oneTempTemplate = oneLogTemplates[int(piece[0])-1]
                    oneRawlog = oneTempTemplate[0]
                    if len(oneTempTemplate)!=1:
                        for a,b in zip(piece[1],oneTempTemplate[1:]):
                            oneRawlog = oneRawlog+a+b
                    oneResult.append(oneRawlog)
                    oneTime1 = time.time()


                    time0 = time.time()
                    logTemplates = [x[x.find("\t")+1:].split("*") for x in logTemplates]
                    for one in tempMatchResults:
                        tempResult = [one[:one.find("\t")],one[one.find("\t")+1:].split(" ")]
                        if tempResult[1][-1]!="" and tempResult[1][-1][-1] == "\n":
                            tempResult[1][-1]=tempResult[1][-1][:-1]
                        matchResults.append(tempResult)
                    for piece in matchResults:                
                        tempTemplate = logTemplates[int(piece[0])-1]
                        oneRawlog = tempTemplate[0]
                        if len(tempTemplate)!=1:
                            for a,b in zip(piece[1],tempTemplate[1:]):
                                oneRawlog = oneRawlog+a+b
                        ourResults.append(oneRawlog)
                    time1 = time.time()

                    with open(resultBasePath+path+"/"+dataset+"/rawlog.log","w") as rawlogFile:
                        rawlogFile.writelines(ourResults)    
                except:
                    result.append([path,dataset,"--","--"])
                    continue
                result.append([path,dataset,round(time1-time0,5),round(oneTime1-oneTime0,5)])
        with open("decompress_our_result.csv","w") as resultFile:
            file_csv = csv.writer(resultFile)
            title = ["algorithm","dataset","all_time","one_log_time"]  
            file_csv.writerow(title)
            file_csv.writerows(result)