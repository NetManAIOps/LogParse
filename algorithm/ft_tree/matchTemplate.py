#!/usr/bin/python
# -*- coding: UTF-8 -*-

from copy import deepcopy
from log_formatter import LogFormatter
import time
import os
import json
import datetime
#from extractFailure import Failure,Log
from ft_tree import getMsgFromNewSyslog
#import numpy as np
import ft_tree





def matchTemplatesAndSave(rawlog_path,template_path,break_threshold=0):
    '''
        计算每个模板匹配的日志的个数
    '''
    new_path=template_path+'order_logTemplate.txt'#words排序后的templates
    tag_temp_dir = {}
    tag_log_dir={}
    tag_count = {}
    # 1.初始化template_list
    print ("reading templates from",template_path+'logTemplate.txt')
    match = Match(template_path+'logTemplate.txt')
    result_dict={}
    for i in range(len(match.template_list)):
        # f=file(template_path+'template'+str(i+1)+'.txt','w')
        result_dict[i+1]=[]
    print ("# of templates:",len(match.template_list))
    cur_ID=0
    f = file(template_path + 'logSequence.txt','w')
    out_list=[]
    n=1
    with open(rawlog_path) as IN:
        for line in IN:
            n+=1
            if n%2000 == 0:
                print( 'cur',n)
            cur_ID+=1
            #2.匹配模板
            line = line.strip()
            l=line.split()
            cur_time=l[0]
            tag=match.matchTemplateByType(line)
            # if tag not in tag_temp_dir:
            #     tag_log_dir[tag]=' '.join(l[1:])
            #     tag_temp_dir[tag]=match.template_list[tag-1]
                #print tag_log_dir[tag]
                #print tag_temp_dir[tag]
                #print ''
                # print ' '.join(l)
                # print "tag:"+str(tag),
                # print match.template_list[tag-1],'\n'

            result_dict[tag].append(cur_ID)
            out_list.append(str(cur_time)+' '+str(tag)+'\n')
            # f.writelines(str(cur_time)+' '+str(tag)+'\n')
            if break_threshold!=0 and cur_ID > break_threshold:
                break

    for line in out_list:
        f.writelines(line)



class Match:


    words_frequency = []
    template_tag_dir = {} #模板号跟模板的对应关系，其中模板是字符串
    log_once_list = []
    template_list = []
    tag_template_dir={} #模板号跟模板的对应关系，其中模板是字符串
    tree = '' # 树(根节点)
    # def __init__(self,template_path):
    #     with open(template_path) as IN:  # SDTemplate.dat
    #         for template in IN:
    #             self.template_list.append(template)

    def __init__(self,para):
        '''
            Return:
                wft:树的根节点
                words_frequency:从文件中读取的词频列表
                template_tag_dir: 模板号跟模板的对应关系，其中模板是字符串
        '''
        template_path = para['template_path']
        match_model = para['match_model']
        #print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&init___template_path:', template_path)
        #print('****************************init___match_model', match_model)
        fre_word_path = para['fre_word_path']
        wft = ft_tree.WordsFrequencyTree()
        tag = 1 #模板号从1 开始
        with open(template_path) as IN:
            for line in IN:
                self.log_once_list.append(['',line.strip().split()])
                #从template文件中读取tag
                #tag = line.strip().split()[0]
                #template = ' '.join(line.strip().split()[1:])
                template = line.strip()
                self.template_tag_dir[template] = tag
                self.tag_template_dir[tag] = template
                tag += 1
        # print(self.tag_template_dir)
        # print('logoncelistlogoncelistlogoncelistlogoncelist-----------------')
        # print(self.log_once_list)


        if match_model == 4:
            #print('4444444444444444444444444444')
            wft.paths = []
            wft._nodes = []
            for words in self.log_once_list:
                wft._init_tree([''])
            wft.auto_temp1(self.log_once_list, para, rebuild=1)
            self.tree = wft
        else:
            #print('not4444444444444444444444444444')
            with open(fre_word_path) as IN:
                for line in IN:
                    self.words_frequency.append(line.strip())
            wft.paths = []
            wft._nodes = []
            for words in self.log_once_list:
                wft._init_tree([''])
            wft.auto_temp(self.log_once_list, self.words_frequency, para, rebuild=1)
            self.tree = wft

    def drawTree(self):

        #draw trees
        if True:
            import pygraphviz as pgv
            A=pgv.AGraph(directed=True,strict=True)
            draw_list=[]
            unique_dir={} #record the times of words
            for pid in self.tree.tree_list:
                # print ('cur_value')
                head_node = self.tree.tree_list[pid]._head
                myQueue = []
                myQueue.append(head_node)
                while myQueue:
                    #之所以没把广度遍历的action放到pop后，是因为在添加节点的同时，各个节点的父节点是同一个
                    node = myQueue.pop(0)
                    cur_data = node.get_data()
                    cur_father = cur_data+' '*node._index
                    for child_node in node.get_children():
                        myQueue.append(child_node)
                        cur_child = child_node.get_data()
                        if cur_child not in unique_dir:
                            unique_dir[cur_child] = 0
                        else:
                            unique_dir[cur_child] += 1
                        child_node._index = unique_dir[cur_child]
                        cur_child = str(cur_child+' '*child_node._index)
                        if cur_father != '':
                            #重建树的时候，不知道哪个单词是被剪枝的,所以没有红色，只有训练阶段画图才知道
                            #蓝色结点包括叶节点和短模板的终点结点
                            if child_node.is_end_node:
                                A.add_node(cur_child,color='blue')
                            else:
                                A.add_node(cur_child)
                            A.add_node(cur_father)
                            A.add_edge(cur_father,cur_child)
                A.write('fooOld.dot')
                A.layout('dot') # layout with dot
                A.draw('reBuildTree.png') # write to file


    def match(self,log_words, match_model=0):
        '''
            输入是list跟string都可以！

            log_words = ft_tree.getMsgFromNewSyslog(log)[1]
            匹配到返回tag，没匹配到返回0

        '''
        #鲁棒，输入str也是可以的
        words = []
        if type(log_words) == type(''):
             log_words = ft_tree.getMsgFromNewSyslog(log_words)[1]

        if match_model == 4:
            for word in log_words:
                words.append(word)
            #print('-------------------no sorting-----------------------')
        else:
            #sort raw log
            words_index = {}
            for word in log_words:
                    if word in self.words_frequency:
                        words_index[word] = self.words_frequency.index(word)
                    # else:
                    #     print(word,'not in the dict')
            words = [x[0] for x in sorted(words_index.items(), key=lambda x: x[1])]
            #print('-------------------after sorting-----------------------')
        #print(words)
        cur_match = []
        cur_node = self.tree.tree_list['']._head
        for word in words:
            if cur_node.find_child_node(word) != None:
                cur_node = cur_node.find_child_node(word)
                cur_match.append(word)
        cur_match = ' '.join(cur_match) #
        # print(cur_match+"\n")
        #匹配不到的话 输出0
        tag = self.template_tag_dir[cur_match] if cur_match in self.template_tag_dir else 0

        return tag, cur_match


    def matchLogsFromFile(self, para):
        '''
         如果没匹配上，会生成0, 原始代码
        '''
        #print('#######################################')
        if para['plot_flag'] == 1:
            #print('#######################################')
            self.drawTree() #画ft-tree


        raw_log_path = para['runtime_log_path']
        out_seq_path = para['out_seq_path']
        short_threshold = para['short_threshold']
        template_path = para['template_path']
        match_model = para['match_model']

        f = open(out_seq_path, 'w')
        short_log = 0
        # short_threshold = 5
        count_zero = 0
        total_num = 0
        with open(raw_log_path) as IN:
            for line in IN:
                total_num += 1
                timestamp = line.strip().split()[0]
                log_words = ft_tree.getMsgFromNewSyslog(line)[1]

                tag,cur_match = self.match(log_words, match_model)
                if len(log_words) < short_threshold:  # 过滤长度小于5的日志
                    short_log += 1
                    tag = -1

                # 匹配到了输出1~n，没匹配到输出0，日志小于过滤长度输出-1
                #输出时间戳
                # f.writelines(timestamp + ' ' + str(tag) + '\n')
                f.writelines(str(tag) + '\n')
                if tag == 0:
                    count_zero += 1
                    # print line



        print('filting # short logs:', short_log, '| threshold =', short_threshold)
        print('# of unmatched log (except filting):', count_zero)
        print('# of total logs:', total_num)
        print('seq_file_path:', out_seq_path)
        # print('template_path:', template_path)


    def matchLogsAndLearnTemplateOneByOne(self, para):
        '''
            增量学习模板
            如果没匹配上，会生成新的模板，然后返回新的模板号
            每条日志单条学习，流式数据学习
        '''
        template_path = para['template_path']
        new_logs_path = para['log_path']
        out_seq_path = para['out_seq_path']
        short_threshold = para['short_threshold']
        match_model = para['match_model']

        f = open(out_seq_path, 'w')
        short_log = 0
        # short_threshold = 5
        count_zero = 0
        total_num = 0
        with open(new_logs_path) as IN:
            for line in IN:
                total_num +=1
                timestamp = line.strip().split()[0]
                log_words = ft_tree.getMsgFromNewSyslog(line)[1]
                tag, cur_match = self.match(log_words, match_model)
                # print (line.strip())
                # print ('~~cur_match:',cur_match)
                # print ('')
                if len(log_words)< short_threshold:#过滤长度小于5的日志
                    short_log+=1
                    tag = -1


                #如果匹配不上，则增量学习模板
                if tag == 0:
                    print ('learned a new template:')
                    count_zero += 1
                    #增量学习
                    # temp_tree=self.tree
                    print(line)
                    cur_log_once_list=[['', log_words]]
                    self.tree.auto_temp(cur_log_once_list, self.words_frequency, para)
                    new_tag = len(self.template_tag_dir)+1

                    #添加完新的模板之后，重新匹配日志，把新的模板match到的文本输出出来
                    tag, cur_match = self.match(log_words)
                    self.template_tag_dir[cur_match]=new_tag
                    self.tag_template_dir[new_tag]=cur_match
                    #第三次匹配模板，输出目前匹配的tag
                    tag, cur_match = self.match(log_words)
#                    self.drawTree()
                    print (tag, cur_match)
                    # print ('')
                    #保存新的模板
                    ff = open(template_path,'a')
                    ff.writelines(str(tag)+' '+cur_match+'\n')
                    ff.close()
                #匹配到了输出1~n，没匹配到输出新增量学习的模板号，日志小于过滤长度输出-1
                f.writelines(timestamp+' '+str(tag)+'\n')

        print ('filting # short logs:',short_log,'| threshold =',short_threshold)
        print ('# of unmatched log (except filting):', count_zero)
        print ('# of total logs:',total_num)
        print ('seq_file_path:',out_seq_path)

        if para['plot_flag'] == 1:
            self.drawTree()



    def LearnTemplateByIntervals(self, para):
        '''
            增量学习模板
            每一时段增量学习一次
        '''
        # print (para)
        template_path = para['template_path']
        new_logs_path = para['log_path']
        leaf_num = para['leaf_num']
        short_threshold = para['short_threshold']
        match_model = para['match_model']


        f = open(template_path, 'a')
        short_log = 0
        count_zero = 0
        total_num = 0
        # print('template_tag_dir:',self.template_tag_dir)


        with open(new_logs_path) as IN:
            for line in IN:
                total_num +=1
                timestamp = line.strip().split()[0]
                log_words = ft_tree.getMsgFromNewSyslog(line)[1]
                tag, cur_match = self.match(log_words, match_model)
                # print (line.strip())
                # print ('~~cur_match:',cur_match)
                # print ('')
                if len(log_words)< short_threshold:#过滤长度小于5的日志
                    short_log+=1
                    tag = -1


                #如果匹配不上，则增量学习模板
                if tag == 0:
                    # print ('learned a new template:')
                    count_zero += 1
                    #增量学习
                    # temp_tree=self.tree
                    cur_log_once_list=[['', log_words]]
                    self.tree.auto_temp(cur_log_once_list, self.words_frequency, para)



       # 遍历特征树,每条路径作为一个模板
        all_paths = {}

        for pid in self.tree.tree_list:
            all_paths[pid] = []
            path = self.tree.traversal_tree(self.tree.tree_list[pid])

            for template in path[1]:
                all_paths[pid].append(template)

            # 大集合优先
            # 有的模板是另外一个模板的子集,此时要保证大集合优先`
            all_paths[pid].sort(key=lambda x: len(x), reverse=True)
        # count=0

        typeList = []
        # 将每条模板存储到对应的pid文件夹中

        i = 1
        print ('new templates:')
        for pid in all_paths:
            for path in all_paths[pid]:
                print (i, pid, end=' ')
                # 首先把pid保存下来
                cur_match =' '.join(path)
                for w in path:
                    print (w, end=' ')
                print ( '')
                i += 1
                # if True:
                if cur_match not in self.template_tag_dir:
                    tag = len(self.template_tag_dir)+1
                    self.template_tag_dir[cur_match]=tag
                    f.writelines(str(tag)+' '+cur_match+'\n')
                    print (cur_match)



        with open(new_logs_path) as IN:
            for line in IN:
                total_num +=1
                timestamp = line.strip().split()[0]
                log_words = ft_tree.getMsgFromNewSyslog(line)[1]
                tag, cur_match = self.match(log_words)
                # print (tag, cur_match)
        if para['plot_flag'] == 1:
            self.drawTree()

        print ('filting # short logs:',short_log,'| threshold =',short_threshold)
        print ('# of unmatched log (except filting):', count_zero)
        print ('# of total logs:',total_num)
        # print ('seq_file_path:',para['out_seq_path'])


def match(para):
    if para['match_model'] != 4:
        mt = Match(para)#template_path, fre_word_path
    if para['match_model'] == 1:
        mt.matchLogsFromFile(para)#按照现有模板匹配日志，匹配不到则设置为0
    elif para['match_model'] == 2:
        mt.matchLogsAndLearnTemplateOneByOne(para)#增量学习模板，每条增量
    elif para['match_model'] == 3:
        mt.LearnTemplateByIntervals(para) #增量学习模板，日志分批增量学习
    elif para['match_model'] == 4:
        #args = parser.parse_args(['-plot_flag', '1', '-template_path', './out_logTemplate_order.txt', '-match_model', '4'])
        para = {
            'short_threshold' : args.short_threshold,
            'leaf_num' : args.leaf_num,
            'template_path' : args.template_path,
            'fre_word_path' : args.fre_word_path,
            'runtime_log_path' : args.runtime_log_path,
            'out_seq_path' : args.out_seq_path,
            'CUTTING_PERCENT' : args.CUTTING_PERCENT,
            'plot_flag' : args.plot_flag,
            'NO_CUTTING' : args.NO_CUTTING,
            'match_model' : args.match_model
        }
        #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@print_help()&&&&&&&&&&&&&&&&&&&&&&&')
        #parser.print_help()
        mt1 = Match(para)
        mt1.matchLogsFromFile(para)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-short_threshold', help='short_threshold', type=int, default=5)
    parser.add_argument('-leaf_num', help='增量学习时的剪枝阈值 ,如果将6改成10，可以看出不同，即LearnTemplateByIntervals会对新来的数据做剪枝', type=int, default=10)
    parser.add_argument('-template_path', help='plot_flag', type=str, default="./output.template_middle")
    parser.add_argument('-fre_word_path', help='fre_word_path', type=str, default="./output.fre")
    parser.add_argument('-runtime_log_path', help='log_path', type=str, default='./training.log')
    parser.add_argument('-out_seq_path', help='out_seq_path', type=str, default='./output.seq')
    parser.add_argument('-plot_flag', help='画图, 如树太大不要画图，会卡死', type=int, default=0)
    parser.add_argument('-CUTTING_PERCENT', help='增量学习时会用到，正常匹配用不到',type=float, default = 0.3)
    parser.add_argument('-NO_CUTTING', help='增量学习时会用到，正常匹配用不到', type=int, default=1)#初步设定1时，是前60% 不剪枝 ,全局开关， 当其为0时，全局按照min_threshold剪枝
    parser.add_argument('-match_model', help='1:正常匹配  2:单条增量学习&匹配 3:批量增量学习&匹配 4:正序匹配', type=int, default = 1)
    args = parser.parse_args()

    para = {
        'short_threshold' : args.short_threshold,
        'leaf_num' : args.leaf_num,
        'template_path' : args.template_path,
        'fre_word_path' : args.fre_word_path,
        'runtime_log_path' : args.runtime_log_path,
        'out_seq_path' : args.out_seq_path,
        'CUTTING_PERCENT' : args.CUTTING_PERCENT,
        'plot_flag' : args.plot_flag,
        'NO_CUTTING' : args.NO_CUTTING,
        'match_model' : args.match_model
    }

    match(para)
    print ('match end~~~')

