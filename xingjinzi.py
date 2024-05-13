
from functools import reduce
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from strsimpy.string_distance import StringDistance


def initDict(path):
    dict = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f.readlines():
            # 移除换行符，并且根据空格拆分
            splits = line.strip('\n').split(' ')
            key = splits[0]
            value = splits[1]
            dict[key] = value
    return dict


# 字典初始化 
bihuashuDict = initDict('LMY/技术标/最终结果/领域数据/错误修改/权重计算/bihuashu_2w.txt')
hanzijiegouDict = initDict('LMY/技术标/最终结果/领域数据/错误修改/权重计算/hanzijiegou_2w.txt')
pianpangbushouDict = initDict('LMY/技术标/最终结果/领域数据/错误修改/权重计算/pianpangbushou_2w.txt')
sijiaobianmaDict = initDict('LMY/技术标/最终结果/领域数据/错误修改/权重计算/sijiaobianma_2w.txt')

# 权重定义（可自行调整）
hanzijiegouRate = 10
sijiaobianmaRate = 8
pianpangbushouRate = 6
bihuashuRate = 2

# 计算核心方法
'''
desc: 笔画数相似度
'''


def bihuashuSimilar(charOne, charTwo):
    valueOne = bihuashuDict[charOne]
    valueTwo = bihuashuDict[charTwo]

    numOne = int(valueOne)
    numTwo = int(valueTwo)

    diffVal = 1 - abs((numOne - numTwo) / max(numOne, numTwo))
    return bihuashuRate * diffVal * 1.0


'''
desc: 汉字结构数相似度
'''


def hanzijiegouSimilar(charOne, charTwo):
    valueOne = hanzijiegouDict[charOne]
    valueTwo = hanzijiegouDict[charTwo]

    if valueOne == valueTwo:
        # 后续可以优化为相近的结构
        return hanzijiegouRate * 1
    return 0


'''
desc: 四角编码相似度
'''


def sijiaobianmaSimilar(charOne, charTwo):
    valueOne = sijiaobianmaDict[charOne]
    valueTwo = sijiaobianmaDict[charTwo]

    totalScore = 0.0
    minLen = min(len(valueOne), len(valueTwo))

    for i in range(minLen):
        if valueOne[i] == valueTwo[i]:
            totalScore += 1.0

    totalScore = totalScore / minLen * 1.0
    return totalScore * sijiaobianmaRate


'''
desc: 偏旁部首相似度
'''


def pianpangbushoutSimilar(charOne, charTwo):
    valueOne = pianpangbushouDict[charOne]
    valueTwo = pianpangbushouDict[charTwo]

    if valueOne == valueTwo:
        # 后续可以优化为字的拆分
        return pianpangbushouRate * 1
    return 0


'''
desc: 计算两个汉字的相似度
'''


def similar(charOne, charTwo):
    if charOne == charTwo:
        return 1.0

    sijiaoScore = sijiaobianmaSimilar(charOne, charTwo)
    jiegouScore = hanzijiegouSimilar(charOne, charTwo)
    bushouScore = pianpangbushoutSimilar(charOne, charTwo)
    bihuashuScore = bihuashuSimilar(charOne, charTwo)

    totalScore = sijiaoScore + jiegouScore + bushouScore + bihuashuScore
    totalRate = hanzijiegouRate + sijiaobianmaRate + pianpangbushouRate + bihuashuRate

    result = totalScore * 1.0 / totalRate * 1.0
    # print('总分：' + str(totalScore) + ', 总权重: ' + str(totalRate) + ', 结果:' + str(result))
    # print('四角编码：' + str(sijiaoScore))
    # print('汉字结构：' + str(jiegouScore))
    # print('偏旁部首：' + str(bushouScore))
    # print('笔画数：' + str(bihuashuScore))
    return result


def default_insertion_cost(char):
    return 1.0


def default_deletion_cost(char):
    return 1.0


def default_substitution_cost(char_a, char_b):
    # print(char_a, char_b,similar(char_a, char_b))
    return 1-similar(char_a, char_b)


class WeightedLevenshtein(StringDistance):

    def __init__(self,
                 substitution_cost_fn=default_substitution_cost,
                 insertion_cost_fn=default_insertion_cost,
                 deletion_cost_fn=default_deletion_cost,
                 ):
        self.substitution_cost_fn = substitution_cost_fn
        self.insertion_cost_fn = insertion_cost_fn
        self.deletion_cost_fn = deletion_cost_fn

    def distance(self, s0, s1):
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0
        if len(s0) == 0:
            return reduce(lambda cost, char: cost + self.insertion_cost_fn(char), s1, 0)
        if len(s1) == 0:
            return reduce(lambda cost, char: cost + self.deletion_cost_fn(char), s0, 0)

        v0, v1 = [0.0] * (len(s1) + 1), [0.0] * (len(s1) + 1)

        v0[0] = 0
        for i in range(1, len(v0)):
            v0[i] = v0[i - 1] + self.insertion_cost_fn(s1[i - 1])

        for i in range(len(s0)):
            s0i = s0[i]
            deletion_cost = self.deletion_cost_fn(s0i)
            v1[0] = v0[0] + deletion_cost

            for j in range(len(s1)):
                s1j = s1[j]
                cost = 0
                if s0i != s1j:
                    cost = self.substitution_cost_fn(s0i, s1j)
                insertion_cost = self.insertion_cost_fn(s1j)
                v1[j + 1] = min(v1[j] + insertion_cost, v0[j + 1] + deletion_cost, v0[j] + cost)
            v0, v1 = v1, v0

        return v0[len(s1)]




str1 = "大"
str2 = "太"
weighted_levenshtein = WeightedLevenshtein()
result = weighted_levenshtein.distance(str1, str2)
print(str1, str2, result, 1 - result / max((len(str1), len(str2))))
