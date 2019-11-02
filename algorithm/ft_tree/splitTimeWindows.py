#!/usr/bin/python
# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import numpy as np

anomaly_start=int(1528022400) #2018-06-03 18:40:00
anomaly_end=int(1528025236) #2018-06-03 19:27:16
seq_path='./ft_tree/err_logSequence.txt'
# seq_path='./ft_tree/out_logSequence.txt'
slot=60*60 #15mins
#TEMP_NUM=702
TEMP_NUM=583
time_tag_dir={}
totol_tag_count_dir={}
anomaly_tag_count_dir={}

def splitWindows(seq_path,save_path,anomaly_start,anomaly_end,slot):
    print 'start'
    time_list=[]
    tag_list=[]
    with open(seq_path) as IN:
        for line in IN:
            l=line.strip().split()
            time_list.append(int(l[0]))
            tag_list.append(int(l[1]))
            #time_tag_dir[l[0]+' '+l[1]]=int(l[0])

    print len(tag_list)
    c_zip = list(zip(tag_list, time_list))
    print len(c_zip)
    sorted_by_value = sorted(c_zip, key=lambda tup: tup[1])
    tag_list,time_list = zip(*sorted_by_value)

    print 'start time of the logSquence:',time_list[0]
    print 'end time of the logSquence:',time_list[-1]

    total_slot_num = (time_list[-1]-time_list[0])/slot+1
    print 'total_slot_num',total_slot_num
    count_dir={}
    for i in range(TEMP_NUM):
        count_dir[i+1]=[] #{tag:[1,2,3,4]}
    cur_slot_start = time_list[0]
    cur_slot_end = cur_slot_start+slot
    cur_count_dir ={}
    gt_list=[] #标记groundtruth中的异常 1异常0正常
    if anomaly_start < cur_slot_end and anomaly_end > cur_slot_start:
        gt_list.append(1)
    else:
        gt_list.append(0)
    for i in range(TEMP_NUM):
        cur_count_dir[i+1]=0 #{tag:count in a slot}

    for i,cur_tag in enumerate(tag_list):
        cur_time = time_list[i]
        cur_count_dir[cur_tag]+=1
        #更新timeslot的信息
        if cur_time>cur_slot_end:
            cur_slot_start += slot
            cur_slot_end += slot
            if anomaly_start < cur_slot_end and anomaly_end > cur_slot_start:
                gt_list.append(1)
            else:
                gt_list.append(0)
            for j in range(TEMP_NUM):
                save_tag=j+1
                count_dir[save_tag].append(cur_count_dir[save_tag])
                cur_count_dir[save_tag]=0
    #保存最后一个timeslot
    if len(count_dir[1])<total_slot_num:
        if anomaly_start < cur_slot_end and anomaly_end > cur_slot_start:
            gt_list.append(1)
        else:
            gt_list.append(0)
        for j in range(TEMP_NUM):
            save_tag=j+1
            count_dir[save_tag].append(cur_count_dir[save_tag])

    print 'len(count_dir)',len(count_dir)
    print 'len(count_dir[1])',len(count_dir[1])


    for tag in count_dir:
        anomaly_tag_count_dir[tag]=0
        totol_tag_count_dir[tag]=sum(count_dir[tag])
    for index,flag in enumerate(gt_list):
        if flag == 1:
            for tag in totol_tag_count_dir:
                anomaly_tag_count_dir[tag]+=count_dir[tag][index]
    healthy_tag_count_dir={}
    for tag in totol_tag_count_dir:
        healthy_tag_count_dir[tag]=totol_tag_count_dir[tag]-anomaly_tag_count_dir[tag]
    total_sorted_tuple=sorted(totol_tag_count_dir.iteritems(), key=lambda asd:asd[1], reverse=True)
    anomaly_sorted_tuple=sorted(anomaly_tag_count_dir.iteritems(), key=lambda asd:asd[1], reverse=True)
    healthy_sorted_tuple=sorted(healthy_tag_count_dir.iteritems(), key=lambda asd:asd[1], reverse=True)




    total_show_dir={}
    healthy_show_dir={}
    anomaly_show_dir={}
    final_show_dir={}
    final_set=set()
    for i,n in enumerate(total_sorted_tuple[:10]):
        tag=n[0]
        final_set.add(tag)
    for i,n in enumerate(anomaly_sorted_tuple[:10]):
        tag=n[0]
        final_set.add(tag)
    for i,n in enumerate(healthy_sorted_tuple[:10]):
        tag=n[0]
        final_set.add(tag)

    final_tag=[]
    final_total=[]
    final_healthy=[]
    final_anomaly=[]
    for i,n in enumerate(total_sorted_tuple):
         tag=n[0]
         num=n[1]
         if tag in final_set:
            final_tag.append(tag)
            final_total.append(num)

    for tag in final_tag:
        for i,n in enumerate(healthy_sorted_tuple):
            cur_tag=n[0]
            num=n[1]
            if tag == cur_tag:
                # print n
                final_healthy.append(num)

    for tag in final_tag:
        for i,n in enumerate(anomaly_sorted_tuple):
            cur_tag=n[0]
            num=n[1]
            if tag==cur_tag:

                final_anomaly.append(num)


    print 'final_tag',final_tag
    print 'final_total',final_total
    print 'final_healthy',final_healthy
    print 'final_anomaly',final_anomaly

    index = np.arange(len(final_tag))
    bar_width = 0.3
    plt.bar(index ,final_total , width=0.3 , color='b',label='total')
    plt.bar(index +  bar_width, final_healthy, width=0.3 , color='y',label='normal',tick_label=final_tag)
    plt.bar(index +  bar_width*2, final_anomaly, width=0.3 , color='g',label='anomaly')
    plt.yscale('log')#y坐标取对数
    # plt.title('')
    plt.legend(loc='upper rigth')
    plt.title('systemout (sorted by total slots)' )
    plt.show()





    ##画3*1的图
    # name_list=[]
    # num_list=[]
    # for i,n in enumerate(total_sorted_tuple[:10]):
    #     name_list.append(n[0])
    #     num_list.append(n[1])
    #     # plt.bar(range(len(num_list)), num_list,color='rgb')
    # plt.subplot(311)
    # plt.bar(range(len(num_list)), num_list,color='rgb',tick_label=name_list)
    # plt.yscale('log')#y坐标取对数
    # plt.title('Top10 templates in Total Slots')
    # plt.xlabel('Templates')
    # plt.ylabel('Frequences')
    # # plt.xticks([])#关闭x坐标

    # name_list=[]
    # num_list=[]
    # for i,n in enumerate(anomaly_sorted_tuple[:10]):
    #     name_list.append(n[0])
    #     num_list.append(n[1])
    #     # plt.bar(range(len(num_list)), num_list,color='rgb')
    # plt.subplot(313)
    # plt.bar(range(len(num_list)), num_list,color='rgb',tick_label=name_list)
    # plt.yscale('log')#y坐标取对数
    # plt.title('Top10 templates in Anomalous Slots')
    # plt.xlabel('Templates')
    # plt.ylabel('Frequences')

    # name_list=[]
    # num_list=[]
    # for i,n in enumerate(healthy_sorted_tuple[:10]):
    #     name_list.append(n[0])
    #     num_list.append(n[1])
    #     # plt.bar(range(len(num_list)), num_list,color='rgb')
    # plt.subplot(312)
    # plt.bar(range(len(num_list)), num_list,color='rgb',tick_label=name_list)
    # plt.yscale('log')#y坐标取对数
    # plt.title('Top10 templates in Normal Slots')
    # plt.xlabel('Templates')
    # plt.ylabel('Frequences')

    # plt.tight_layout(h_pad=1.2)#w_pad是调整子图之间的宽间距
    # plt.show()

    print 'top 10 total_sorted_tuple:'
    print total_sorted_tuple[:10]
    print 'top 10 anomaly:'
    print anomaly_sorted_tuple[:10]
    print 'top 10 healthy:'
    print healthy_sorted_tuple[:10]

    #输出成文本文件
    with open(save_path, 'w') as f:
        f.write('slots')
        for i in range(TEMP_NUM):
            f.write(' t_'+str(i+1))
        f.write('\n')
        na={1:'a',0:'n'}
        for time_slot_index in range(total_slot_num):
            f.write(str(na[gt_list[time_slot_index]])+'_'+str(time_slot_index+1))
            for i in range(TEMP_NUM):
                tag=i+1
                f.write(' '+str(count_dir[tag][time_slot_index]))
            f.write('\n')




if __name__ == '__main__':
    save_path=str(slot)+'err_timeSlotCount.txt'
    splitWindows(seq_path,save_path,anomaly_start,anomaly_end,slot)
    print 'end'


