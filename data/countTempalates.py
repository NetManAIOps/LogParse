#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os

for a, dirs, filenames in os.walk('./'):
    for cur_dir in dirs:
        print('cur_dir',cur_dir)
        index_list = []
        template_list = []
        for i in range(1000):
            i += 1
            cur_filename = cur_dir+'/template' + str(i) + '.txt'
            try:
                with open(cur_filename) as IN:
                    for line in IN:
                        l = line.strip().split()
                        template_list.append(i)
                        index_list.append(int(l[0]))
                #print(' ',cur_filename)
            #如果没有template文件了 则跳出
            except:
                print(' # of unique templates:', i-1)
                break
        c_zip = list(zip(index_list, template_list))
        sorted_by_value = sorted(c_zip, key=lambda tup: tup[0])
        sorted_index, sorted_template = zip(*sorted_by_value)

        #分析前1000与后1000的区别
        former_dict = {}
        former_set = set()
        latter_dict = {}
        latter_set = set()
        for index, template in zip(sorted_index, sorted_template):
            index = int(index)
            template = int(template)
            if index <= 1000:
                if template not in former_dict:
                    former_set.add(template)
                    former_dict[template] = 0
                former_dict[template] += 1
            else:
                if template not in latter_dict:
                    latter_dict[template] = 0
                    latter_set.add(template)
                latter_dict[template] += 1
        diff_set = latter_set - former_set
        intersection_set = latter_set&former_set
        print(' former:',len(former_set),'latter:', len(latter_set),'diff_in_latter:',len(diff_set), 'inter set:', len(intersection_set))

        #保存序列文件
        f = open(cur_dir + '/groundtruth.seq', 'w')
        for a, b in zip(sorted_index, sorted_template):
            f.writelines(str(a) + ' ' + str(b) + '\n')





