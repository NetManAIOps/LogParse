#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
from ft_tree import getMsgFromNewSyslog


def orderTemplate(para):
    rawlog = para['rawlog']
    templates = para['templates']
    sequences = para['sequences']
    order_templates = para['order_templates']
    variable_symbol = para['variable_symbol']


    tag_index={}
    index_tag={}
    tag_temp={}
    tag_log={}

    index=0
    with open(sequences) as IN:
        for line in IN:
            tag = line.strip()
            # print(tag)
            if tag not in tag_index:
                #print(tag)
                tag_index[tag]=index
                index_tag[index]=tag
            index+=1


    index=0
    with open(rawlog) as IN:
        for line in IN:
            if index in index_tag:
                tag_log[index_tag[index]]=line.strip()
            index+=1

    tag=1
    with open(templates) as IN:
        for line in IN:
            tag_temp[str(tag)]=line.strip()
            tag+=1

    f=open(order_templates,'w')
    for i in range(len(tag_temp)):
        tag=str(i+1)
        out=' '.join(list(set(tag_temp[tag].split())))
        if tag in tag_log:
            # find the correspondent raw log
            log=getMsgFromNewSyslog(tag_log[tag])[1]
            # print(log)
            # find the correspondent template
            temp=tag_temp[tag].split()
            new_temp=[]
            for k in log :
                if k in temp:
                    new_temp.append(k)
                    temp.remove(k)
            # modify the template
            out=' '.join(new_temp)
        f.writelines(out+'\n')
    print('template_path', order_templates)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-middle_templates', help='templates', type=str, default="./output.template_middle")
    parser.add_argument('-sequences', help='sequences', type=str, default="./output.seq")
    parser.add_argument('-rawlog', help='rawlog', type=str, default="./training.log")
    parser.add_argument('-final_templates', help='rawlog', type=str, default="./output.template")
    parser.add_argument('-variable_symbol', help='输出模板时，用*表示模板中的变量空位', type=str, default=" ")
    args = parser.parse_args()

    para = {
    'rawlog': args.rawlog,
    'templates': args.middle_templates,
    'sequences' : args.sequences,
    'order_templates' : args.final_templates,
    'variable_symbol' : args.variable_symbol
    }
    
    orderTemplate(para)
    print('ordered')









