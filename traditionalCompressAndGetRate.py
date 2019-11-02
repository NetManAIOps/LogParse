#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# Get compress rate of algorithms.
import os
import csv
import sys
import lzma
import gzip
import bz2
import time
import threading

basePath = "./"
dataPath=basePath+"data/"
resultPath=basePath+"results/logTIM_results/"

results = []
# ans = []
tempans=[]

# ------ compress
def deal_fileName(fileName):
    length=len(fileName)
    for i in range(length):
        if fileName[length-1-i]==".":
            return fileName[:length-1-i]

def time_func(function):
    def inner(sourceFile,destFile,*args,**kwargs):
        global tempans
        sourceSize = os.path.getsize(sourceFile)
        t0=time.time()
        function(sourceFile,destFile)
        t1=time.time()
        destSize = os.path.getsize(destFile)
        # ans.append([round(t1-t0,5),round(destSize/sourceSize,5),function.__name__,sourceFile])
        tempans=[sourceSize,destSize]
    return inner


@time_func
def compress_bzip2(sourceFile,destFile):
    with bz2.BZ2File(destFile, 'wb') as des:
        with open(sourceFile, 'rb') as sou:
            des.writelines(sou)

@time_func
def compress_7zip(sourceFile,destFile):
    os.system("7z a -t7z {destfile} {sourcefile}".format(destfile=destFile,sourcefile=sourceFile))

@time_func
def compress_zip(sourceFile,destFile):
    os.system("7z a -tzip {destfile} {sourcefile}".format(destfile=destFile,sourcefile=sourceFile))


def deal_argv(argv):
    global tempans
    global results
    try:
        with open(argv[1],mode="r") as f:
            pass
    except:
        print("Source file does not exist.")
        return
    if argv[0] == "bz2":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".bz2")
        elif argv[2][-4:]!=".bz2":
            argv[2]=argv[2]+".bz2"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:
            compress_bzip2(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/tempans[0],5)])
    elif argv[0] == "7z":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".7z")
        elif argv[2][-3:]!=".7z":
            argv[2]=argv[2]+".7z"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:            
            compress_7zip(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/tempans[0],5)])
    elif argv[0] == "zip":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".zip")
        elif argv[2][-4:]!=".zip":
            argv[2]=argv[2]+".zip"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:
            compress_zip(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/tempans[0],5)])
    else:
        # print("Usage: compressWay source_file_name dest_file_name.compressWay")
        print("error")


def deal_argv_match(argv,sourceSize):
    global tempans
    global results
    try:

        with open(argv[1],mode="r") as f:
            pass
    except:
        print("Source file does not exist.")
        return
    if argv[0] == "bz2":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".bz2")
        elif argv[2][-4:]!=".bz2":
            argv[2]=argv[2]+".bz2"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:
            compress_bzip2(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/sourceSize,5)])
    elif argv[0] == "7z":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".7z")
        elif argv[2][-3:]!=".7z":
            argv[2]=argv[2]+".7z"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:        
            compress_7zip(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/sourceSize,5)])
    elif argv[0] == "zip":
        if len(argv)==2:
            argv.append(deal_fileName(argv[1])+".zip")
        elif argv[2][-4:]!=".zip":
            argv[2]=argv[2]+".zip"
        if os.path.exists(argv[2])==True:
            tempans = [os.path.getsize(argv[1]),os.path.getsize(argv[2])]
        else:
            compress_zip(argv[1],argv[2])
        results[-1].extend([tempans[1],round(tempans[1]/sourceSize,5)])
    else:
        # print("Usage: compressWay source_file_name dest_file_name.compressWay")
        print("error")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compressAndGetRate.py [all] [match] [first] [second] [[1-9]|all]")    
    else:
        tempSysargvs = sys.argv
        if tempSysargvs[1] == "all":
            wayargvs = ["match","first","second"]
        else:
            wayargvs = tempSysargvs[1:-1]
        if tempSysargvs[-1]=="all":
            tempDir = "_tail"
        else:
            tempDir = "_tail_0."+tempSysargvs[-1]+"0"
        tempPaths = os.listdir(dataPath)
        rawlogPaths = [x for x in tempPaths if tempDir in x]
        rawlogInfo = {}
        for i in rawlogPaths:
            temp = i.split("_tail")
            tempPath = temp[0]+temp[1]
            rawlogInfo[tempPath] = {"size":os.path.getsize(dataPath+i+"/rawlog.log"),"path":dataPath+i+"/rawlog.log","judge":0}
        algPaths = os.listdir(resultPath)


        for path in algPaths:
            tempList = os.listdir(resultPath+path)
            for subPath in rawlogInfo.keys():
                tempPath = resultPath+path+"/"+subPath+"/matchResults.txt"
                sourceSize = rawlogInfo[subPath]["size"]
                results.append([path,subPath,sourceSize])
                if "match" in wayargvs:
                    try:
                        matchResultsSize = os.path.getsize(tempPath)
                        results[-1].extend([matchResultsSize,round(matchResultsSize/sourceSize,5)])
                    except:
                        results[-1].extend(["--","--"])
                ways = ["bz2","7z","zip"]
                if "first" in wayargvs:
                    for way in ways:
                        tempargv=[way,rawlogInfo[subPath]["path"]]
                        deal_argv(tempargv)
                if "second" in wayargvs:
                    for way in ways:
                        tempargv=[way,tempPath]
                        deal_argv_match(tempargv,rawlogInfo[subPath]["size"])
        csvPath = "result_"+tempSysargvs[1]+"_"+tempSysargvs[2]+".csv"     
        with open(csvPath,"w") as f:
            f_csv = csv.writer(f)
            row = ["algorithm","dataset","sourceSize"]
            if "match" in wayargvs:
                row.extend(["matchResultsSize","matchResults_rate"])
            if "first" in wayargvs:
                row.extend(["bz2","bz2_rate","7z","7z_rate","zip","zip_rate"])
            if "second" in wayargvs:
                row.extend(["double_bz2","double_bz2_rate","double_7z","double_7z_rate","double_zip","double_zip_rate"]) 
            f_csv.writerow(row)
            f_csv.writerows(results)


            
