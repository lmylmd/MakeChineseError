import pypinyin
import Pinyin2Hanzi
import random,string
import os,json,re
import tqdm
import numpy as np

from xingjinzi import WeightedLevenshtein
def random_lmy(left,right):
    if right==0:
        return 0
    if(left>=right):
        return right
    else:
        return random.randint(left,right)
#针对拼音去找字
def gainHanzi(listPinyin:list,goal,errornummin,errornummax):
    n_Zi=random_lmy(errornummin,errornummax)#修改几个汉字错误
    for i in range(0,n_Zi):
        dagParams = Pinyin2Hanzi.DefaultDagParams()
        where=random_lmy(0,len(listPinyin)-1)
        # 10个候选值
        result = Pinyin2Hanzi.dag(dagParams, [listPinyin[where]], path_num=3, log=True)
        goal=list(goal)
        if len(result)>0:
            try:
                whitch=random_lmy(1,max(len(result)-1,1)) if len(result)>0 else 0    
                goal[where]=result[whitch].path[0]
            except:
                pass
    end=''.join(goal)
    return end
#同音字扰动
def tongyinzi(s,errornummin,errornummax):
    s=gainHanzi(pypinyin.lazy_pinyin(s),s,errornummin,errornummax)
    return s


# 定义一个包含随机字符的列表，包括中文、英文、数字等
chinese_chars = ''
#english_chars = string.ascii_letters
english_chars = ''
#digit_chars = string.digits
digit_chars = ''
punctuation = '，。！？、；：“”…·\'"'
all_chars = chinese_chars + english_chars + digit_chars+punctuation

# 定义一个函数来随机删除标点符号
def random_punctuation_removal(text,errornummin,errornummax):
    # 定义包含中英文标点符号的字符串
    punctuation = r"，。！？、；：“”…·\'\""
    # 使用正则表达式找到所有标点符号
    punctuations_to_remove = re.findall('[' + punctuation + ']', text)
    # 如果文本中没有标点符号，返回原始文本
    if not punctuations_to_remove:
        return text
    # 从所有可移除的标点符号中随机选择一个数量进行移除
    num_to_remove = random_lmy(errornummin, min(len(punctuations_to_remove),errornummax))
    # 随机选择要移除的标点符号
    punctuations_to_remove = random.sample(punctuations_to_remove, num_to_remove)
    # 创建一个新的字符串，删除选择的标点符号
    new_text = ''
    for char in text:
        if char in punctuations_to_remove:
            punctuations_to_remove.remove(char)
        else:
            new_text += char
    return new_text

def random_insert(text,errornummin,errornummax,all_chars =punctuation):
    """
    在文本中随机插入指定数量的随机字符。
    
    :param text: 原始文本
    :param insert_count: 要插入的随机字符的数量
    :return: 添加了扰动后的文本
    """
    insert_count=random_lmy(errornummin,errornummax)
    text = list(text)
    text_length = len(text)
    
    for _ in range(insert_count):
        # 随机选择一个字符
        random_char = random.choice(all_chars)
        # 随机选择插入的位置
        insert_pos = random_lmy(0, text_length)
        # 将字符插入到随机位置
        text.insert(insert_pos, random_char)
    
    return ''.join(text)



#标点扰动     
def biaodian(s,errornummin,errornummax):
    s=random_insert(s,errornummin,errornummax//2)
    s= end=random_punctuation_removal(s,errornummin,errornummax//2)
    return s

def remove_random_characters(input_string,errornummin,errornummax):
    # 确定输入字符串的长度
    str_len = len(input_string)
    
    # 判断字符串是否为空
    if str_len == 0:
        return ''
    # 随机决定删除的字符个数
    num_chars_to_remove = random_lmy(errornummin, min(errornummax,str_len))
    # 生成一个随机位置索引的列表
    indexes_to_remove = random.sample(range(str_len), num_chars_to_remove)
    # 创建一个新字符串，包含未被删除的字符
    new_string = ''.join(
        char for idx, char in enumerate(input_string) if idx not in indexes_to_remove
    )
    return new_string

def duozishaozi(s,errornummin,errornummax):
    s=random_insert(s,errornummin,errornummax//2)
    s=remove_random_characters(s,errornummin,errornummax//2)
    return s

def xingjinzi(s,errornummin,errornummax):
    
    with open("LMY/技术标/最终结果/领域数据/错误修改/常用汉字库 3500.txt",'r',encoding='utf-8-sig') as f:
        chars=f.read()
    for j in range(random_lmy(errornummin,errornummax)):
        if len(s)<=1:
            continue
        str1='|'
        while (str1 not in chars) :
            where=random_lmy(0,max(1,len(s)-1))
            str1 = s[where]
        houxuan=[]
        for k in range(len(chars)):
            weighted_levenshtein = WeightedLevenshtein()
            result = weighted_levenshtein.distance(str1, chars[k])
            houxuan.append([chars[k],1 - result / max((len(str1), len(chars[k])))])
        sorted_dict_list = sorted(houxuan, key=lambda x: x[1], reverse=True)
        s=list(s)
        s[where]=sorted_dict_list[random_lmy(0,min(8,len(sorted_dict_list)-1))][0]
    s=''.join(s)
    return s
def main(dir1,dir2,inputoutput,nums):
    with open(dir1,'r',encoding='utf-8') as f:
        data=json.load(f)
    for i in tqdm.tqdm(range(len(data)), desc='遍历中'):
        if i==1013:
            pass
        s=data[i][inputoutput[0]]
        #s=tongyinzi(s,nums[0][0],nums[0][1])
        s=biaodian(s,nums[1][0],nums[1][1])
        s=duozishaozi(s,nums[2][0],nums[2][1])
        s=xingjinzi(s,nums[3][0],nums[3][1])
        data[i][inputoutput[1]]=s
    with open(dir2,'w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))

main("LMY/技术标/最终结果/领域数据/错误修改/input_answer1.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer1234.json",['output','input'],[[1,2],[1,2],[1,2],[1,2]])
        
