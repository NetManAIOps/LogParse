#!/usr/bin/python
# -*- coding: UTF-8 -*-

# SYSTEM LIBS
import threading, time
import os
import os.path
import sys
from copy import deepcopy
from log_formatter import LogFormatter
import time
import os
import re
import json
import datetime
from aggregateTemplate import aggregateTemplate


# from myMatchFailure import calculateRandIndex
# from Tree import Tree, traversal_tree

# reload(sys)
# sys.setdefaultencoding('utf8')



__all__ = []
FIRST_COL = 0
DRAWTREE = 0
max_org = 0


class Node(object):
    """ Node of tree

    """
    _level = 0 #初始化为0
    _index =0 #初始化为0， 为了在画图的时候得到unique node
    _father = '' #head节点的father是空字符串，其他节点的父节点都是Node类型的变量
    _no_cutting = 0 #初步设定是前60% 不剪枝，如果no_cutting为0，则正常节点，若no_cutting==1，则该节点不减枝
    def __init__(self, data):
        """ Constructor for Node """
        super(Node, self).__init__()
        self._data = data

        self._children = []
        # 用于判断经过该节点的路径是否超过10条，如果是，将该节点改成叶结点，其值设置为1
        self._change_to_leaf = 0

        # 用户判断该节点是否是一条路径的最后一个节点
        # 主要针对的场景是一条模板是另外一条模板的子集
        self.is_end_node = 0

    def get_data(self):
        """获取节点数据
        Returns:
        """
        return self._data

    def get_children_num(self):
        """ 获取该节点的子节点的数量

        Returns:

        """
        return len(self._children)

    def get_children(self):
        """ 获取所有子节点

        Returns:

        """
        return self._children

    def delete_children(self):
        """ 删除所有的子节点

        Returns:

        """
        self._change_to_leaf = 1
        for child in self._children:
            child = []

        self._children = []

    def add_child_node(self, node, leaf_num=10, cut_level=3, rebuild=0):
        """
        Args:
            node: Node对象,子节点
            rebuild: 0代表创建树阶段，1代表匹配模板是重构树
        Returns:
        """
        global max_org
        # 10个叶子节点会剪枝
        # 根节点不受剪枝限制
        node._level=self._level+1
        # if self._level>cut_level and len(self._children) == leaf_num: #超过10个节点剪枝
        if max_org < len(self._children):
            max_org = len(self._children)

        if self._level>cut_level and len(self._children) == leaf_num and self._no_cutting != 1 and rebuild == 0:
        # if self._level>cut_level and len(self._children) == leaf_num and self.get_data() != 'org': #超过10个节点剪枝
            self.delete_children()
            return False 

        if self._change_to_leaf == 1:
            return False

        node._father = self
        self._children.append(node)

    def find_child_node(self, data):
        """ 查找包含当前节点,包含data的子节点
        Args:
            data: data
        Returns:
        """

        for child in self._children:
            if child.get_data() == data:
                return child

        return None


class Tree(object):
    """ Template tree

    """
    # self.visited = {}#for dfs
    def __init__(self, head):
        """ Init a tree """
        super(Tree, self).__init__()

        """一般来讲,pid会作为一个数的根节点"""
        self._head = Node(head)
        self._head._level=1

    def link_to_head(self, node, leaf_num=10):
        """ 设置树的根节点

        Args:
            node:

        Returns:

        """
        self._head.add_child_node(node, leaf_num)


    def insert_node(self, path, data, para, is_end_node=0, no_cutting=0, rebuild=0):
        """ 向树种插入一个节点,该节点挂在path的末端

        Args:
            path: 节点的父目录
            data: 节点数据
            no_cutting: 该节点不剪枝 ，如果no_cutting==1，则该节点不减枝
        Returns:

        """
        NO_CUTTING = 0
        if rebuild == 0:
            NO_CUTTING = para['NO_CUTTING']
        leaf_num = para['leaf_num']

        cur = self._head
        for step in path:
            if cur._change_to_leaf == 1:
                return False
            if not cur.find_child_node(step):
                return False
            else:
                cur = cur.find_child_node(step)

        for child in cur.get_children():
            if child.get_data() == data:
                if child.is_end_node == 0:
                    child.is_end_node = is_end_node
                return False

        new_node = Node(data)
        if rebuild == 1:
            new_node._no_cutting = 1
        elif no_cutting and NO_CUTTING:
            new_node._no_cutting = 1
        new_node.is_end_node = is_end_node
        cur.add_child_node(new_node, leaf_num)

        return True

    def search_path(self, path):
        """ 查找路径

        Args:
            path: 要查找的路径, a list.

        Returns:

        """
        cur = self._head

        for step in path:
            if not cur.find_child_node(step):
                return None
            else:
                cur = cur.find_child_node(step)
        return cur


class WordsFrequencyTree(object):
    """

    """

    def __init__(self):
        """
        Returns:

        """
        self.tree_list = {}  # 保存所有树的字典{pid:树的对象}

    def _init_tree(self, pids):
        """ Init tree

        Args:
            pids: All pids of syslog

        Returns:

        """
        self.tree_list = {}

        for pid in pids:
            tree = Tree(pid)
            self.tree_list[pid] = tree

    def _traversal(self, subtree, path, sub_path):
        """
        """

        subs = subtree.get_children()

        if not subs:
            path.append(self._nodes)
            self._nodes = self._nodes[:-1]
            return None
        else:
            if subtree.is_end_node == 1:
                _path = tuple(deepcopy(self._nodes))
                sub_path.append(_path)
                subtree.is_end_node = 0

            for n in subs:
                self._nodes.append(n.get_data())
                self._traversal(n, path, sub_path)
            self._nodes = self._nodes[:-1]

    def traversal_tree(self, tree):
        """ 遍历多叉树，获取模板列表
        """
        _nodes, path, sub_path = [], [], []

        path.append(tree._head.get_data())

        self._traversal(tree._head, path, sub_path)

        path.extend(sub_path)
        _path = [tuple(x) for x in path[1:]]

        return [path[0], list(set(_path))]

    def auto_temp(self, logs, words_frequency, para, rebuild=0):
        """

        Args:
            pids: pids of all syslog
            lines: 分词后的集合
            words_frequency: 词频列表
            rebuild: 0 模板提取， 1 fttree重建

        Returns:

        """
        leaf_num = para['leaf_num']
        CUTTING_PERCENT = 0
        # print ('rebuild',rebuild)
        if rebuild == 0:
            CUTTING_PERCEN = para['CUTTING_PERCENT']


        assert logs != []
        assert words_frequency != []
        # global  CUTTING_PERCENT
        #
        # if CUTTING_PERCENT=='':
        #     CUTTING_PERCENT=0
        #保留重复单词
        # words_index = {}
        # words_count = {}
        for log in logs:
            pid, words = log
            words = list(set(words))#过滤掉重复的单词set
            # print('-----------words_before_sorted-----------------')
            # print(words)
            words_index = {}
            words_count = {}
            for word in words:
                if word in words_frequency:
                    words_index[word] = float(words_frequency.index(word))
                #统计重复的单词
                if word not in words_count:
                    words_count[word]=0
                words_count[word]+=1

            for word in words_count:
                if words_count[word]>1:
                    print('words_count[word]>1')
                    cur_word=word
                    for i in range(words_count[word]-1):
                        cur_word= cur_word+' '+word
                    words_index[cur_word] = words_index[word]
                    # print cur_word
                    # print word
                    words_index.pop(word)

        
            words = [x[0] for x in sorted(words_index.items(), key=lambda x: x[1])]
            words_len = len(words)
            words = ' '.join(words).split()
            # print('----------------words-----------------')
            # print(words)

            # print len(words)
            for index, value in enumerate(words):
                no_cutting = 0 #0一切正常，按照leafnum剪枝，1不剪枝
                if rebuild == 1: #表示matchTemplate中调用函数重新建树
                    no_cutting = 1 #如果重新建树，则所有的节点都不减枝
                elif index<=float(len(words))*CUTTING_PERCENT:
                    no_cutting = 1
                if index == words_len - 1:
                    # self.tree_list[pid].insert_node(words[:index], value, 0, leaf_num, no_cutting, rebuild)# 暂时去掉模板子集的限制，即不检测最后一个结点了，即只保留长模板
                    self.tree_list[pid].insert_node(words[:index], value, para, 1, no_cutting, rebuild) #检测最后一个节点！ 保留短模板
                else:
                    self.tree_list[pid].insert_node(words[:index], value, para, 0, no_cutting, rebuild)


        #过滤掉重复的单词
        # for log in logs:
        #     pid, words = log
        #     words = list(set(words))#过滤掉重复的单词

        #     words_index = {}
        #     for word in words:
        #         if word in words_frequency:
        #             words_index[word] = words_frequency.index(word)

        #     words = [x[0] for x in sorted(words_index.items(), key=lambda x: x[1])]
        #     words_len = len(words)

        #     for index, value in enumerate(words):
        #         if index == words_len - 1:
        #             # 暂时去掉模板子集的限制，即不检测最后一个结点了
        #             self.tree_list[pid].insert_node(words[:index], value, 0, leaf_num)
        #             # self.tree_list[pid].insert_node(words[:index], value, 1,leaf_num)
        #         else:
        #             self.tree_list[pid].insert_node(words[:index], value, 0, leaf_num)


    def auto_temp1(self, logs, para, rebuild=0):
        """

        Args:
            pids: pids of all syslog
            lines: 分词后的集合
            words_frequency: 词频列表
            rebuild: 0 模板提取， 1 fttree重建

        Returns:

        """
        leaf_num = para['leaf_num']
        CUTTING_PERCENT = 0
        # print ('rebuild',rebuild)
        if rebuild == 0:
            CUTTING_PERCEN = para['CUTTING_PERCENT']


        assert logs != []
        # assert words_frequency != []
        for log in logs:
            pid, words = log
            words = list(words)#过滤掉重复的单词set
            print(words)
            words_index = {}
            words_count = {}
            for word in words:
            #     if word in words_frequency:
            #         words_index[word] = float(words_frequency.index(word))
                #统计重复的单词
                if word not in words_count:
                    words_count[word]=0
                words_count[word]+=1
            for k, v in words_index.items():
                print(k, v)

            for word in words_count:
                if words_count[word]>1:
                    print('words_count[word]>1')
                    cur_word=word
                    for i in range(words_count[word]-1):
                        cur_word= cur_word+' '+word
                    words_index[cur_word] = words_index[word]
                    # print cur_word
                    # print word
                    words_index.pop(word)

            #======================anzhaocipin paixulog
            # words = [x[0] for x in sorted(words_index.items(), key=lambda x: x[1])]
            words_len = len(words)
            words = ' '.join(words).split()
            # print('----------------1words-----------------')
            # print(words)

            # print len(words)
            for index, value in enumerate(words):
                no_cutting = 0 #0一切正常，按照leafnum剪枝，1不剪枝
                if rebuild == 1: #表示matchTemplate中调用函数重新建树
                    no_cutting = 1 #如果重新建树，则所有的节点都不减枝
                elif index<=float(len(words))*CUTTING_PERCENT:
                    no_cutting = 1
                if index == words_len - 1:
                    # self.tree_list[pid].insert_node(words[:index], value, 0, leaf_num, no_cutting, rebuild)# 暂时去掉模板子集的限制，即不检测最后一个结点了，即只保留长模板
                    self.tree_list[pid].insert_node(words[:index], value, para, 1, no_cutting, rebuild) #检测最后一个节点！ 保留短模板
                else:
                    self.tree_list[pid].insert_node(words[:index], value, para, 0, no_cutting, rebuild)


    def do(self, logs, para):
        """
        Args:
            pids: a list, pid 集合
            logs: a list, 日志集合,包含pid和分词结果
            date: 保存date,用于将不同日期的模板保存到不同的文件中
            last_templates: 上一轮迭代的模板
            last_words_fre: 上一轮迭代的词频
            fre_word_path: 保存单词频率的文件路径

        Returns:
            all_paths: a dict, 包含了特征树的所有路径,每一条路径是一个模板
            words_frequency: a list, 包含了本轮迭代的词频结果
        """

        template_path = para['template_path']
        fre_word_path = para['fre_word_path']
        leaf_num = para['leaf_num']
        CUTTING_PERCENT = para['CUTTING_PERCENT']
        plot_flag = para['plot_flag']

        if not logs:
            return {}

        self.paths = []
        self._nodes = []

        lines, pids = [], []
        words_frequency = {}

        for log in logs:
            (pid, words) = log
            if pid not in pids:
                pids.append(pid)
            lines.append(log)  # lines保存（pid,words）的元组，其实就是logs，这个变量的存在没有意义

            # 统计词频
            for w in words:
                # if len(w) == 1:  # 单个字母的词无意义
                #     continue
                if w not in words_frequency:
                    words_frequency[w] = 0

                words_frequency[w] += 1

        """ 按照词频进行排序,从高到低
        高频度的词具有较高的权重,应该处在父节点的位置
        """
        words_frequency = sorted(words_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True)
        words_frequency = [x[0] for x in words_frequency]


        f = open(fre_word_path, 'w')
        for w in words_frequency:
            f.writelines(w+'\n')

        self._init_tree(pids)
        self.auto_temp(lines, words_frequency, para)
        #self.auto_temp(lines, words_frequency, leaf_num, CUTTING_PERCENT=CUTTING_PERCENT)

        if plot_flag == 1:
            #画树，dratTreee，画图，放到输出模板之前，是因为traversal_tree函数会修改is_end变量的值，存在bug！！
            self.drawTree()#画树，dratTreee，画图



        # 遍历特征树,每条路径作为一个模板
        all_paths = {}

        for pid in self.tree_list:
            all_paths[pid] = []




            path = self.traversal_tree(self.tree_list[pid])

            for template in path[1]:
                all_paths[pid].append(template)

            # 大集合优先
            # 有的模板是另外一个模板的子集,此时要保证大集合优先`
            all_paths[pid].sort(key=lambda x: len(x), reverse=True)
        # count=0

        typeList = []



        # 将每条模板存储到对应的pid文件夹中
        f = open(template_path, 'w')
        i = 1
        for pid in all_paths:
            for path in all_paths[pid]:
                # count+=1
                #print (i, pid)
                print (i, pid, end=' ')
                # 首先把pid保存下来
                f.write(pid + " ") #不保存index
                #f.write(str(i)+' '+pid + " ")#保存index，从1开始
                for w in path:
                    #print (w)
                    print (w, end=' ')
                    f.write(w + " ")
                print ( '')
                f.write("\n")
                i += 1
        f.close()
        # print "\ntemplate_count:",count
        return all_paths

    def drawTree(self):
        #draw trees
        import pygraphviz as pgv
        A=pgv.AGraph(directed=True,strict=True)
        draw_list=[]
        unique_dir={} #record the times of words
        for pid in self.tree_list:
            head_node = self.tree_list[pid]._head
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
                    cur_child = cur_child+' '*child_node._index
                    if cur_father != '':
                        # print cur_child,child_node.is_end_node
                        if child_node.is_end_node:
                            A.add_node(cur_child,color='blue')
                        else:
                            A.add_node(cur_child)

                        if child_node._change_to_leaf:
                            A.add_node(cur_child,color='red') #标记剪枝


                        A.add_node(cur_father)
                        A.add_edge(cur_father,cur_child)
            A.write('fooOld.dot')
            A.layout('dot') # layout with dot
            A.draw('Trace.png') # write to file


def RecursionPreOrder(node):
    if(node is not None):
        print(node.get_data())
        for child_node in node.get_children():
            RecursionPreOrder(node)


def getMsgFromNewSyslog(log, msg_id_index=3):
    '''
        //从newsyslog中拆分单词，过滤数字、变量，获得pid和word_list
        return : (msg_root,word_list)
    '''

    # word_list = log.strip().split()
    # msg = ' '.join(word_list[FIRST_COL:])
    msg = log

    #正则表达式
    # msg = re.sub('(:(?=\s))|((?<=\s):)', ' ', msg)
    # # msg = re.sub('(\d+\.)+\d+', '', msg)
    # # msg = re.sub('\d{2}:\d{2}:\d{2}', '', msg)
    # # msg = re.sub('Mar|Apr|Dec|Jan|Feb|Nov|Oct|May|Jun|Jul|Aug|Sep', '', msg)
    # # msg = re.sub(':?(\w+:)+', '', msg)
    # msg = re.sub('\.|\(|\)|\<|\>|\/|\-|\=|\[|\]|,|:', ' ', msg)
    # msg = re.sub('\\b(0[xX])?[A-Fa-f0-9]+\\b', ' ', msg)#过滤十六进制的内存地址
    msg = re.sub('\s?(\s|^)[1-9]\d*(\s|$)\s?', ' ', msg)#过滤连续的纯数字

    msg_list = msg.split()

    if len(msg_list)>300:
        msg_list=msg_list[:300]

    #暂时将msg_root设置为空
    msg_root=''
    # print msg_list
    return (msg_root, msg_list)


def getLogsAndSave(para):
    '''
        e为跳出的阈值
        return : log_list,log_num
    '''

    path = para['data_path']
    output_name = para['template_path']
    fre_word_path = para['fre_word_path']
    leaf_num = para['leaf_num']
    short_threshold = para['short_threshold']


    short_log=0
    n = 0
    log_once_list = []
    flag = 0
    wft = WordsFrequencyTree()
    # print path,date
    lft = LogFormatter()
    with open(path) as IN:
        n = 1
        for log in IN:
            n += 1
            log = log.strip()
            if not log:
                continue
            return_msg=getMsgFromNewSyslog(log)
            
            if len(return_msg[1]) < short_threshold: #过滤长度小于5的日志
                short_log+=1
                continue
            log_once_list.append(getMsgFromNewSyslog(log))

    print ('creating template')
    # print len(log_once_list)
    wft.do(log_once_list, para)
    print ('filting # short logs:',short_log,'| threshold =',short_threshold)
    print ('template_path:', output_name)
    print ('fre_word_path:', fre_word_path)




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-FIRST_COL', help='FIRST_COL', type=int, default=0)#表示日志数据从第几列开始，若纯logs，则为0
    parser.add_argument('-NO_CUTTING', help='NO_CUTTING', type=int, default=1)#初步设定1时，是前30% 不剪枝 ,全局开关， 当其为0时，全局按照min_threshold剪枝
    parser.add_argument('-CUTTING_PERCENT', help='CUTTING_PERCENT',type=float, default=0.3)
    parser.add_argument('-train_log_path', type=str, default='./training.log')
    parser.add_argument('-template_path', type=str, default='./output.template')
    parser.add_argument('-fre_word_path', type=str, default='./output.fre')
    parser.add_argument('-picture_path', type=str, default='./tree.png')
    parser.add_argument('-leaf_num', type=int, default=4)
    parser.add_argument('-short_threshold', type=int, default=5)#过滤掉长度小于5的日志
    parser.add_argument('-plot_flag', help='画图, 如树太大不要画图，会卡死', type=int, default=0)#如果要画图 则为1
    args = parser.parse_args()

    para = {
        'FIRST_COL' : args.FIRST_COL,
        'NO_CUTTING' : args.NO_CUTTING,
        'CUTTING_PERCENT' : args.CUTTING_PERCENT,
        'data_path' : args.train_log_path,
        'template_path' : args.template_path,
        'fre_word_path' : args.fre_word_path,
        'leaf_num' : args.leaf_num,
        'picture_path' : args.picture_path,
        'short_threshold' : args.short_threshold,
        'plot_flag' : args.plot_flag
    }

    if True:
        getLogsAndSave(para)
        print ('leaf_num',para['leaf_num'])
        print ('max_org',max_org)
        print (str(para['CUTTING_PERCENT']*100)+'% nodes are not cut' if para['NO_CUTTING'] else 'all nodes are cut')
    print ("training finished")








