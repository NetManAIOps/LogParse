#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
import json
import os
import re
import sys
import signal
import string

'''
try:
    from jpype import *
except ImportError as e:
    print e
    os._exit(-1)
   
jar_libs = []
jar_libs.append(os.path.join("./jar", "MyTokenizer.jar"))
jar_libs.append(os.path.join("./jar", "lucene-analyzers-common-5.3.1.jar"))
jar_libs.append(os.path.join("./jar", "lucene-core-5.3.1.jar"))

class_path = ":".join(jar_libs)
startJVM("/Library/Java/JavaVirtualMachines/jdk1.8.0_73.jdk/Contents/Home/jre/lib/server/libjvm.dylib", '-ea', '-Djava.class.path=%s' % class_path)
#!!!!!JAVA1.8µƒjvm∏˙1.6≤ª“ª—˘£¨–Ë“™¥”Contents/Home/jre/lib/server¿Ô’“
TA = JPackage('tokenizer').MyTokenizer
jd = TA()
'''
class LogFormatter(object):
    def tokenizer(self,msg):
        """
        Args:
        Returns:
        """
        msg = re.sub('\d', ' ', msg)
        msg = re.sub('Mar|GMT|Apr', '', msg)
        msg = re.sub(':|\.', ' ', msg)
        msg = re.sub('<', ' ', msg)
        msg = re.sub('>', ' ', msg)
        words=msg.split()
        return words
        
        
    #     tokenizer_workders = list(jd.Tokenizer(msg))
    #     return tokenizer_workders
    
    def my_strip(self,body, fmt=" .,:%*"):
        """
        Args:
            body:
            fmt:
    
        Returns:
    
        """
    
        try:
            body = re.sub("MAC\s\w{4}\.\w{4}\.\w{4}", "", body)
            body = body.strip(fmt)
            return body
        except:
            raise

    #getMsg的返回值类型是元组 （switch_type,word_list）
    def getMsg(self,log):
        '''
        return :∑µªÿ“ª∏ˆ‘™◊È(switch_type,words_list)
                    »Áπ˚÷ª–Ë“™words_list  π”√getMsg()[1]
        '''
        switch_type=log['switch_type']
        switch_name=log['switch_name']
        date=log['date']
        mip=log['mip']
        area_type=log['area_type']
        msg=log['msg']
        idc=log['idc']
        
        
        msg = re.sub(switch_name, '', msg)
        msg = re.sub(date, '', msg)
        msg = re.sub(mip, '', msg)
        msg = re.sub(area_type, '', msg)
        msg = re.sub(idc, '', msg)
        msg = re.sub(switch_type, '', msg)
        #msg=re.sub('(Mar|Apr|Dec|Jan|Feb)\s+\d{2}\s+\d{2}:\d{2}:\d{2}', '', msg)
        
        #==========================
        msg = re.sub('(:(?=\s))|((?<=\s):)', '', msg)
        msg = re.sub('(\d+\.)+\d+', '', msg)
        msg = re.sub('\d{2}:\d{2}:\d{2}', '', msg)
        msg = re.sub('Mar|Apr|Dec|Jan|Feb|Nov|Oct|May|Dec', '', msg)
        msg = re.sub(':?(\w+:)+', '', msg)
        msg = re.sub('\d+', '', msg)

        msg=msg.strip()
        words=msg.split()
#         words = list(jd.Tokenizer(msg))
        return (switch_type,words)
    
    def getLogs(self,path,date,e=100):#"/Users/baidu/documents/workspace/baidu_syslog/src/file/2016-04-01/events-.1459440014158"
        '''
            return : log_list,log_num
        '''
        
        n=0
        log_once_list=[]
        log_list=[]
        flag=0
        wft=WordsFrequencyTree()
        with open(path) as IN:
            for log in IN:
                log = log.strip()
                log = re.sub("\d+(\.\d)?$", "", log)
                log = log.strip()
                log = json.loads(log)
                if not log:
                    continue
                #getMsg()∑µªÿ“ª∏ˆ‘™◊È(switch_type,words_list)
                log_once_list.append(self.getMsg(log))
                
                n+=1
                if n>e:
                    n=0
                    flag=1
                    wft.do(log_once_list,dd)
                    log_once_list=[]
                    print (path,'cut list')
            
            wft.do(log_once_list,dd)
#                log_list.append(log_once_list)

#         print "input_count:",n
        return log_list,n
        
    
if __name__ == "__main__":
    l=LogFormatter()
    l.getLogs("events-.1459440014158",10)
    pass

    
