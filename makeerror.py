import pypinyin
import Pinyin2Hanzi
import random,string
import os,json,re
import tqdm
import numpy as np

from xingjinzi import WeightedLevenshtein
#针对拼音去找字
def gainHanzi(listPinyin:list,goal):
    n_Zi=random.randint(1,3)#修改几个汉字错误
    for i in range(0,n_Zi):
        dagParams = Pinyin2Hanzi.DefaultDagParams()
        where=random.randint(0,len(listPinyin)-1)
        # 10个候选值
        result = Pinyin2Hanzi.dag(dagParams, [listPinyin[where]], path_num=3, log=True)
        goal=list(goal)
        if len(result)>0:
            try:
                whitch=random.randint(1,max(len(result)-1,1)) if len(result)>0 else 0    
                goal[where]=result[whitch].path[0]
            except:
                pass
    end=''.join(goal)
    return end
#同音字扰动
def tongyinzi(dir1,dir2,inputoutput):
    with open(dir1,'r',encoding='utf-8') as f:
        data=json.load(f)
    for i in tqdm.tqdm(range(len(data)), desc='同音词'):
        goal=data[i][inputoutput[0]]
        end=gainHanzi(pypinyin.lazy_pinyin(goal),goal)
        end=''.join(end)
        data[i][inputoutput[1]]=end
    with open(dir2,'w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))

# 定义一个包含随机字符的列表，包括中文、英文、数字等
chinese_chars = ''
#english_chars = string.ascii_letters
english_chars = ''
#digit_chars = string.digits
digit_chars = ''
punctuation = '，。！？、；：“”…·\'"'
all_chars = chinese_chars + english_chars + digit_chars+punctuation

# 定义一个函数来随机删除标点符号
def random_punctuation_removal(text, prob=0.2):
    # 定义包含中英文标点符号的字符串
    punctuation = r"，。！？、；：“”…·\'\""

    # 将标点符号替换为空字符，根据给定的概率
    def remove(match):
        # 以给定概率删除标点符号
        if np.random.rand() < prob:
            return ''
        else:
            return match.group(0)

    # 使用正则表达式查找并随机删除标点符号
    return re.sub(punctuation, remove, text)

def random_insert(text,all_chars =punctuation,num=2):
    """
    在文本中随机插入指定数量的随机字符。
    
    :param text: 原始文本
    :param insert_count: 要插入的随机字符的数量
    :return: 添加了扰动后的文本
    """
    insert_count=random.randint(0,num)
    text = list(text)
    text_length = len(text)
    
    for _ in range(insert_count):
        # 随机选择一个字符
        random_char = random.choice(all_chars)
        # 随机选择插入的位置
        insert_pos = random.randint(0, text_length)
        # 将字符插入到随机位置
        text.insert(insert_pos, random_char)
    
    return ''.join(text)



#标点扰动     
def biaodian(dir1,dir2,inputoutput):
    with open(dir1,'r',encoding='utf-8') as f:
        data=json.load(f)
    for i in tqdm.tqdm(range(len(data)), desc='标点符号扰动'):
        goal=data[i][inputoutput[0]]
        end=random_insert(goal)
        end=random_punctuation_removal(end, prob=0.2)
        data[i][inputoutput[1]]=end
    with open(dir2,'w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))

def remove_random_characters(input_string):
    # 确定输入字符串的长度
    str_len = len(input_string)
    
    # 判断字符串是否为空
    if str_len == 0:
        return ''
    # 随机决定删除的字符个数
    num_chars_to_remove = random.randint(1, min(3,str_len))
    # 生成一个随机位置索引的列表
    indexes_to_remove = random.sample(range(str_len), num_chars_to_remove)
    # 创建一个新字符串，包含未被删除的字符
    new_string = ''.join(
        char for idx, char in enumerate(input_string) if idx not in indexes_to_remove
    )
    return new_string

def duozishaozi(dir1,dir2,inputoutput):
    with open(dir1,'r',encoding='utf-8') as f:
        data=json.load(f)
    for i in tqdm.tqdm(range(len(data)), desc='多字少字'):
        goal=data[i][inputoutput[0]]
        end=random_insert(goal,goal)
        end=remove_random_characters(end)
        data[i][inputoutput[1]]=end
    with open(dir2,'w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))

def xingjinzi(dir1,dir2,inputoutput):
    with open(dir1,'r',encoding='utf-8') as f:
        data=json.load(f)
    with open("LMY/技术标/最终结果/领域数据/错误修改/常用汉字库 3500.txt",'r',encoding='utf-8-sig') as f:
        chars=f.read()
    for i in tqdm.tqdm(range(len(data)), desc='形近字扰动'):
        goal=data[i][inputoutput[0]]
        for j in range(3):
            if len(goal)<=1:
                continue
            str1='|'
            while (str1 not in chars) :
                where=random.randint(0,max(1,len(goal)-1))
                str1 = goal[where]
            houxuan=[]
            for k in range(len(chars)):
                weighted_levenshtein = WeightedLevenshtein()
                result = weighted_levenshtein.distance(str1, chars[k])
                houxuan.append([chars[k],1 - result / max((len(str1), len(chars[k])))])
            sorted_dict_list = sorted(houxuan, key=lambda x: x[1], reverse=True)
            goal=list(goal)
            goal[where]=sorted_dict_list[random.randint(0,min(8,len(sorted_dict_list)-1))][0]
        goal=''.join(goal)
        data[i][inputoutput[1]]=goal
    with open(dir2,'w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
def hebing():
    # tongyinzi("LMY/技术标/最终结果/领域数据/错误修改/input_answer.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer1.json",['output','input'])#同音字
    # biaodian("LMY/技术标/最终结果/领域数据/错误修改/input_answer.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer2.json",['output','input'])#标点错误
    # duozishaozi("LMY/技术标/最终结果/领域数据/错误修改/input_answer.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer3.json",['output','input'])#多字少字
    # xingjinzi("LMY/技术标/最终结果/领域数据/错误修改/input_answer.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer4.json",['output','input'])#形近字错误
    
    # with open("LMY/技术标/最终结果/领域数据/错误修改/input_answer1.json",'r',encoding='utf-8') as f:
    #     data1=json.load(f)
    # with open("LMY/技术标/最终结果/领域数据/错误修改/input_answer2.json",'r',encoding='utf-8') as f:
    #     data2=json.load(f)
    # with open("LMY/技术标/最终结果/领域数据/错误修改/input_answer3.json",'r',encoding='utf-8') as f:
    #     data3=json.load(f)
    # with open("LMY/技术标/最终结果/领域数据/错误修改/input_answer4.json",'r',encoding='utf-8') as f:
    #     data4=json.load(f)
    # with open("LMY/技术标/最终结果/领域数据/错误修改/input_answer_all.json",'w',encoding='utf-8') as f:
    #     f.write(json.dumps(data1+data2+data3+data4,ensure_ascii=False,indent=4))
        
    biaodian("LMY/技术标/最终结果/领域数据/错误修改/input_answer1.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer12.json",['input','input'])
    duozishaozi("LMY/技术标/最终结果/领域数据/错误修改/input_answer12.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer123.json",['input','input'])#多字少字
    xingjinzi("LMY/技术标/最终结果/领域数据/错误修改/input_answer123.json","LMY/技术标/最终结果/领域数据/错误修改/input_answer1234.json",['input','input'])#形近字错误

hebing()