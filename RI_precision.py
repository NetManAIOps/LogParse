#coding=utf-8
from numpy import *
import re
from glob import *
import math
#**********************PARAMETERS SETTING*************************************************************
# Parameters could be setted when this function be invoked by other scripts.
# This script is used to calculate the TP, TN, FP, FN, Precision, Recall, F_measure, RI, which utilize
# the method in http://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-clustering-1.html
#*****************************************************************************************************

class prePara:
	def __init__(self,groundTruthDataPath='',logName='rawlog.log',groundTruthTempName='templates.txt',
	groundTruthGroupNamePat='template',geneDataPath='',geneTempName='logTemplates.txt',geneGroupNamePat='template',beta=1):
		print("groundTruthDataPath:", groundTruthDataPath)
		self.groundTruthDataPath=groundTruthDataPath
		self.logName=logName
		self.groundTruthTempName=groundTruthTempName
		self.groundTruthGroupNamePat=groundTruthGroupNamePat
		self.geneDataPath=geneDataPath
		self.geneTempName=geneTempName
		self.geneGroupNamePat=geneGroupNamePat
		self.beta=beta
		
def process(prePara):
	logNum=0
	with open(prePara.groundTruthDataPath+prePara.logName) as lines:
		for line in lines:
			logNum+=1
	print(prePara.groundTruthDataPath+prePara.logName)
	
	gtLogLabel=-1*ones((logNum,1))   #index start from 0,初始时是-1的矩阵

	# t=set()
	# for i in list(gtLogLabel):
	# 	# print i[0]
	# 	t.add(i[0])
	# print("gtLogLabel_set:",t)

    #获取groundtruth
	print("gtLogLabel(all elements are -1):", gtLogLabel.shape)
	gtfilepath=prePara.groundTruthDataPath+prePara.groundTruthGroupNamePat
	gtfileNum=len(glob(gtfilepath+'[0-9]*.txt'))#glob() 函数返回匹配指定模式的文件名或目录
	print ('GT clusters are altogether',gtfileNum, 'files')
	gtLogNumOfEachGroup=zeros((gtfileNum,1))
    #(filepath文件地址,gtLogLabel保存的是每条log_ID对应的label,fileNum模板文件数,gtLogNumOfEachGroup保存的是属于i号模板的日志数量)
	getGtLabel(gtfilepath,gtLogLabel,gtfileNum,gtLogNumOfEachGroup)#获取groundtruth

	#process the groups that produced by algorithm
	geneFilePath=prePara.geneDataPath+prePara.geneGroupNamePat
	fileNum=len(glob(geneFilePath+'[0-9]*.txt'))
	geneClusterLabel=list()  
	#geneClusterLabel is a list of dictionary, for each group by algorithm, 
	#it has a dictionary, with key of ID, value of label from groundtruth
	geneLogNumOfEachGroup=zeros((fileNum,1))
	print ('Result clusters are altogether',fileNum, 'files')
	#for logs in each generated templates, count that for each templates file,
    # the number of each different labels of logs.

    #因为来源是同一个gt类别(同一个gtFile)，又被算法分到了同一个类别，即geneFile中。
    # 所以求一下算法分类的每个类别中数量n的 C(n,2)即为所有分类正确的数量
	for i in range(fileNum):
		filename=geneFilePath+str(i+1)+'.txt'
		labelDict=dict() #记录对应算法分好的类别i中，每个groundtruth_label类别中logs的数量
		count=0
		with open(filename) as lines:
			for line in lines:
				count+=1
				ID = int(line.split('\t')[0])
				label=int(gtLogLabel[ID-1])
				if label not in labelDict:
					labelDict[label]=1
				else:
					labelDict[label]+=1
			geneLogNumOfEachGroup[i]=count#
		geneClusterLabel.append(labelDict)# list(每个算法分类的类别i中，dict(每个groundtruth_label类别中logs的数量))

	TP_FP=0 #被算法分到每个templates里的logs， C(n,2)表示两两组合，已经被分到一个组了，可能被分对，也可能被分错，所以是TP+FP
	for i in range(fileNum):
		if geneLogNumOfEachGroup[i]>1:
			TP_FP+=nCr(geneLogNumOfEachGroup[i],2)#calculate the combination number of C(n,r)

	TP_FN=0#groundtruth中每个templates里的logs， C(n,2)表示两两组合，属于同一个label，算法可能分对TP，也可能分错FN，所以是TP+FN
	for i in range(gtfileNum):
		if gtLogNumOfEachGroup[i]>1:
			TP_FN+=nCr(gtLogNumOfEachGroup[i],2)

	TP=0
	for i in range(len(geneClusterLabel)):# list(每个算法分类的类别i中，dict(每个groundtruth_label类别中logs的数量))
		labelD=geneClusterLabel[i]
		for key,value in labelD.items():
			if value>1:
				TP+=nCr(value,2)

	TP_FP_TN_FN=nCr(logNum,2)
	FN=TP_FN-TP
	FP=TP_FP-TP
	TN=TP_FP_TN_FN-TP_FP-FN
	#print ('TP_FP,TP_FN,TP_FP_TN_FN',TP_FP,TP_FN,TP_FP_TN_FN)
	print ('TP,FP,TN,FN are:',TP,FP,TN,FN)
	precision=float(TP)/(TP_FP)
	recall=float(TP)/(TP_FN)
	b=prePara.beta
	F_measure=float(b*b+1)*precision*recall/(b*b*precision+recall)
	RI=float(TP+TN)/TP_FP_TN_FN
	print ('precision is %.4f'%(precision))
	print ('recall is %.4f'%(recall))
	print ('F measure is %.4f'%(F_measure))
	print ('RI is %.4f'%(RI))
	return TP,FP,TN,FN,precision,recall,F_measure,RI

#open the ground truth data and use the templates name that range from 1 as the label of each log
def getGtLabel(filePath,gtLogLabel,fileNum,gtLogNumOfEachGroup):
	#getGtLabel(filepath文件地址,gtLogLabel初始时是日志数*1的-1矩阵,fileNum模板文件数,gtLogNumOfEachGroup文件数*1的零矩阵)

	for i in range(fileNum):
		count=0
		filename=filePath+str(i+1)+'.txt' #
		with open(filename) as lines:
			label=i+1
			for line in lines:
				count+=1
				ID = int(line.split('\t')[0])
				gtLogLabel[ID-1]=label #gtLogLabel保存的是每条log_ID对应的label
		gtLogNumOfEachGroup[i]=count  #gtLogNumOfEachGroup保存的是属于i号模板的日志数量

#calculate the combination number of C(n,r)
def nCr(n,r):
	result = 1
	denominator = r
	numerator = n
	for i in range(r):
		result *= float(numerator)/denominator
		denominator -= 1
		numerator -= 1
	return result

# preParameters=prePara()
# process(preParameters)
