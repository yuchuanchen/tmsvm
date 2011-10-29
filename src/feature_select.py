#!/usr/bin/python
#author:张知临 zhzhl202@163.com
#Filename: feature_select.py

'''利用卡方进行特征选择的程序'''

import math
import pickle
from fileutil import read_dic

#stopword_filename = "D:/张知临/源代码/python_ctm/Dictionary/im_info/stopwords.txt"
#stopword_filename = "G:/x项目/Taobao/源代码/python_ctm/Dictionary/im_info/stopwords.txt"

def feature_select(filename,indexes,dic_save_path,ratio,stop_words_dic,str_splitTag,tc_splitTag):
    '''特征选择的主函数，输入的训练样本，内容的index，特征选择后的词典保存的路径及名称，卡方选择的比例默认为40%.
    最终会选择top $ratio 的作为最终的词典。
    '''
    dic,cat_num_dic,rows=cons_dic(filename,indexes,stop_words_dic,str_splitTag=str_splitTag,tc_splitTag=tc_splitTag)
    chi_score = chi_max_score(dic,cat_num_dic,rows)
    sorted_keys=sorted(chi_score.items(),key=lambda chi_score:chi_score[1],reverse=True)
    save_keys(sorted_keys[0:int(len(chi_score)*ratio)],dic_save_path)

def cons_dic(filename,indexes,stop_words_dic,str_splitTag,tc_splitTag):
    '''构造词典，主要是为了计算卡方的特征值。
       词典的形式：{term:{label:tf}}
       label 为int型
    '''
    dic =dict() #词典
    #label =dict() #类标签词典，主要是为了查询
    cat_num_dic =dict() #各个类别的个数 
    
    rows = 0 #总的样本个数
    count=0
    f= file(filename,'r')
    for line in f.readlines():
        sample = line.strip().split(tc_splitTag)
        if len(sample)<=indexes[len(indexes)-1]:
            continue
        count+=1
        rows+=1 #统计样本的总行数
        #统计各个样本的个数
        label = int(float(sample[0]))
        if cat_num_dic.has_key(label) is True:
            cat_num_dic[label]+=1.0
        else:
             cat_num_dic[label]=1.0
        #组合所有的内容
        string =""
        string = sample[indexes[0]]
        if len(indexes)>1:
            for i  in range(1,len(indexes)):
                string += str_splitTag+sample[indexes[i]]
               
        for term in string.strip().split(str_splitTag):
            if len(term.strip())==0:
                continue
            term = term.strip()
            if stop_words_dic.has_key(term) is True:
                continue
            if dic.has_key(term) is True:
                if dic[term].has_key(label):
                    dic[term][label]+=1
                else:
                    dic[term][label]=1
            else:
                dic[term]={}
                dic[term][label]=1
    for key in dic.keys():
        for cat in cat_num_dic.keys():
            if dic[key].has_key(cat) is False:
                dic[key][cat]=0.0
    f.close()          
    return dic,cat_num_dic,rows

def chi_max_score(dic,cat_num_dic,rows):
    '''利用卡方公式计算每个term的分值'''
    term_score=dict()
    for term in dic.keys():
        term =term.strip()
        all_num_term = float(sum(dic[term].values()))
        all_num_cat = float(sum(cat_num_dic.values()))
        chi_score= 0.0
        for cat in cat_num_dic.keys():
            A  =  float(dic[term][cat])
            B = float(all_num_term-A)
            C= float(cat_num_dic[cat]-A)
            D = float(all_num_cat-B)
            if (A+C)*(B+D)*(A+B)*(C+D) ==0:
                chi_score=0
            else:
                chi_score = max(chi_score,rows*math.pow(A*D-B*C,2)/((A+C)*(B+D)*(A+B)*(C+D)))
        term_score[term]=chi_score
    return term_score

def chi_avg_score(dic,cat_num_dic,rows):
    '''利用卡方公式计算每个term的分值'''
    term_score=dict()
    for term in dic.keys():
        all_num_term = float(sum(dic[term].values()))
        all_num_cat = float(sum(cat_num_dic.values()))
        chi_score= 0.0
        for cat in cat_num_dic.keys():
            A  =  float(dic[term][cat])
            B = float(all_num_term-A)
            C= float(cat_num_dic[cat]-A)
            D = float(all_num_cat-B)
            chi_score += (float(cat_num_dic[cat])/all_num_cat)*rows*math.pow(A*D-B*C,2)/((A+C)*(B+D)*(A+B)*(C+D))
        term_score[term]=chi_score
    return term_score

def save_keys(keys_truple,save_path):
    '''the format of the key :keys,index,frequant'''  
    f = file(save_path,'w')
    count=0
    for truple in keys_truple:
        count+=1
        f.write(truple[0].strip()+"\t"+str(count)+"\n")
    f.close()

def save_score(score_dic,save_path):
    f = file(save_path,'w')
    for key in score_dic.keys():
        f.write(key.strip()+"\t"+str(score_dic[key])+"\n")
    f.close() 

def save_dic(dic,save_path): 
    pickle.dump(dic,open(save_path,'w')) 
    
def load_dic(load_path):
    return pickle.load(open(load_path,'r'))

def main():
    filename = "D:/张知临/源代码/python_ctm/model/im_info/trainset(4000).train"
    indexes  = [6,7,8,9,10]
    dic_save_path = "D:/张知临/源代码/python_ctm/model/im_info/chi_score.key"
    ratio = 0.4
    feature_select(filename,indexes,dic_save_path,ratio)
    

    