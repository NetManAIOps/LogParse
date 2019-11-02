#!/usr/bin/python
# -*- coding: UTF-8 -*-

# SYSTEM LIBS
import threading, time
import os
import os.path
import sys
from copy import deepcopy
from log_formatter import LogFormatter
import ft_tree
import matchTemplate
import time
import os
import re
import json
import datetime
from aggregateTemplate import aggregateTemplate
import orderWords



if __name__ == "__main__":
    import argparse
    #1.调用ft-tree.py训练模板 ft_tree的参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-FIRST_COL', help='FIRST_COL', type=int, default=0)#表示日志数据从第几列开始，若纯logs，则为0
    parser.add_argument('-NO_CUTTING', help='NO_CUTTING', type=int, default=1)#初步设定1时，是前30% 不剪枝 ,全局开关， 当其为0时，全局按照min_threshold剪枝
    parser.add_argument('-CUTTING_PERCENT', help='CUTTING_PERCENT',type=float, default=0.3)
    parser.add_argument('-train_log_path', type=str, default='./training.log')
    parser.add_argument('-middle_templates', type=str, default='./output.template_middle')
    parser.add_argument('-fre_word_path', type=str, default='./output.fre')
    parser.add_argument('-picture_path', type=str, default='./tree.png')
    parser.add_argument('-leaf_num', type=int, default=5)
    parser.add_argument('-short_threshold', type=int, default=5)#过滤掉长度小于5的日志
    parser.add_argument('-plot_flag', help='画图, 如树太大不要画图，会卡死', type=int, default=0)#如果要画图 则为1
     
    #2.
    # parser.add_argument('-runtime_log_path', help='log_path', type=str, default='./training.log') #'./new.log'
    parser.add_argument('-out_seq_path', help='out_seq_path', type=str, default='./output.seq')
    parser.add_argument('-match_model', help='1:正常匹配  2:单条增量学习&匹配 3:批量增量学习&匹配 4:正序匹配', type=int, default = 1)

    #3 排序
    parser.add_argument('-templates', help='rawlog', type=str, default="./output.template")
    parser.add_argument('-variable_symbol', help='输出模板时，用*表示模板中的变量空位', type=str, default=" ")

    args = parser.parse_args()

    para_train = { 
        'FIRST_COL' : args.FIRST_COL,
        'NO_CUTTING' : args.NO_CUTTING,
        'CUTTING_PERCENT' : args.CUTTING_PERCENT,
        'data_path' : args.train_log_path, 
        'template_path' : args.middle_templates,
        'fre_word_path' : args.fre_word_path,
        'leaf_num' : args.leaf_num,
        'picture_path' : args.picture_path,
        'short_threshold' : args.short_threshold,
        'plot_flag' : args.plot_flag
    }

    para_generate = {
        'short_threshold' : args.short_threshold,
        'leaf_num' : args.leaf_num,
        'template_path' : args.middle_templates,
        'fre_word_path' : args.fre_word_path,
        'runtime_log_path' : args.train_log_path,
        'out_seq_path' : args.out_seq_path,
        'CUTTING_PERCENT' : args.CUTTING_PERCENT,
        'plot_flag' : args.plot_flag,
        'NO_CUTTING' : args.NO_CUTTING,
        'match_model' : args.match_model
    }

    para_order = {
        'rawlog': args.train_log_path,
        'templates': args.middle_templates,
        'sequences' : args.out_seq_path,
        'order_templates' : args.templates,
        'variable_symbol' : args.variable_symbol
    }
    #训练日志模板
    print('-----------training--------------------')
    ft_tree.getLogsAndSave(para_train)
    
    #匹配当前模板
    print('\n----------generating templates-------')
    matchTemplate.match(para_generate)
    #日志模板排序,输出模板文件
    orderWords.orderTemplate(para_order)








