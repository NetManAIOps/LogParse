#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
#import matplotlib
import matplotlib.pyplot as plt

rawlogPath='./env-itsm-was-systemerr0603.log'
logSeqPath='./ft_tree/err_logSequence.txt'
templatePath='./ft_tree/err_logTemplate.txt'
out_path='./err_top10/'

# rawlogPath='./env-itsm-was-systemerr0603.log'
# logSeqPath='./ft_tree/err_logSequence.txt'
# templatePath='./ft_tree/err_logTemplate_order.txt'
countDir={}
with open(logSeqPath) as IN:
    for line in IN:
        l=line.strip().split()
        tag=l[1]
        if tag not in countDir:
            countDir[tag]=0
        countDir[tag]+=1

sorted_final_tuple=sorted(countDir.iteritems(),key=lambda asd:asd[1] ,reverse=True)


# #画所有模板频率分布（柱状图）

# name_list=[]
# num_list=[]
# for i,n in enumerate(sorted_final_tuple[:10]):
#     name_list.append(n[0])
#     num_list.append(n[1])
# # plt.bar(range(len(num_list)), num_list,color='rgb')
# plt.bar(range(len(num_list)), num_list,color='rgb',tick_label=name_list)
# plt.yscale('log')#y坐标取对数
# # plt.xticks([])#关闭x坐标
# plt.title('systemout0603 Top10 templates in all logs')
# plt.show()



#保存Top 10的模板 并且输出每条模板对应的日志文件
top10_temp_dir={}# {tag:template}
temp_list=[]
with open(templatePath) as IN:
    for line in IN:
        temp_list.append(line.strip())
print 'top10 templates:'
for i in range(11):
    tag=sorted_final_tuple[i][0]
    top10_temp_dir[tag]=temp_list[int(tag)-1]
    print tag,countDir[tag],top10_temp_dir[tag]
print ''
index=0
save_dir={}#记录了top10 templates对应的{日志行数(index):tag}
with open(logSeqPath) as IN:
    for line in IN:
        l=line.strip().split()
        tag=l[1]
        if tag in top10_temp_dir:
            save_dir[index]=tag
        index+=1
#tag_log={}#{tag:rawlog_list[]}
f_dir={}#{tag:file_iter}
for tag in top10_temp_dir:
    f=file(out_path+str(tag)+'.txt','w')
    f_dir[tag]=f
index=0
temp_list=[]
f=file(out_path+'top10_templates.txt','w')
for i in range(11):
    tag=sorted_final_tuple[i][0]
    num=sorted_final_tuple[i][1]
    f.writelines(str(tag)+' '+str(num)+' '+top10_temp_dir[tag]+'\n')
with open(rawlogPath) as IN:
    for log in IN:
        if index in save_dir:
            tag=save_dir[index]
            cur_template=top10_temp_dir[tag]
            if tag not in temp_list:
                temp_list.append(tag)
                print tag,cur_template
                print log.strip()
                print '\n'

            f_dir[tag].writelines(cur_template+'\n')
            f_dir[tag].writelines(log+'\n')
        index+=1
print 'end'

