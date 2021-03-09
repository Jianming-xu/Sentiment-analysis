# Accuracy：97.1%
# 最优参数如下
# terms_len = 5  # 参选最短词长度（选入sentiment_terms的最短词长度）参考sentimentPDF 3
# terms_occur = 1  # 参选最低词频（在整个car_opinions中出现的最小次数）参考sentimentPDF 3
# side_ratio = 0.765  # same side ration 同向率：某个词在其得分对应label下的出现比率，参考sentimentPDF 4.2

terms_len = 5
terms_occur = 1

side_ratio = 0.765  # same side ration
terms_side = {}  # same side frquency {word:[Pos times, Neg times]} 储存在正负评价中分别的出现次数
word_siderate = {}  # 词同向率字典
sentiment_terms = {}  # 评分词列表
train_i = range(2)  # 玄学参数，别问这是在干啥，问就是玄学

for i in train_i:  # 玄学循环 你把train_i = range(2) 改成 range(1)再跑一遍
    for line in open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\car_opinions.csv', 'r',
                     encoding='UTF-8'):
        line = line.split(',')  # 分离label与review
        label = line[0]
        review = line[1].split(' ')  # 对review进行分词
        sentiment_score = 1
        if label == 'Neg':
            sentiment_score = -1
        for word in set(review):  # set(review) 使用集合去除重复词
            if word not in terms_side:
                terms_side[word] = [0, 0]  # 不准确赋值法
                # 训练两次时，准确率97%,一次时92%,主要是因为第一次有些词没有选取到，参考40行左右
                # if sentiment_score == 1:
                #     terms_side[word] = [1, 0]
                # else:
                #     terms_side[word] = [0, 1]  # 此处如果用这里的代码（准确赋值法），不会出现玄学现象，但准确率只有95.4%
                # 为什么循环两次不准确赋值法会提高准确率？95.44 -》 97.1
                # 评分词容量提高了！10138 -> 10737
                # 准确赋值法会丢弃一些词！根据后面的代码，只有同向率低于标准的才会被筛选
                # 所以可以推断，准确赋值法使六百多个词的同向率偏低了，或者不准确赋值法会提高这些词的同向率
                # 这六百个词是什么？
            else:
                if sentiment_score == 1:
                    terms_side[word][0] += 1
                else:
                    terms_side[word][1] += 1  #
            if terms_side[word][0] == 0 and terms_side[word][1] == 0:
                word_siderate[word] = 0
                # 不准确赋值法，如果只训练一次，整个数据集只出现过一次的词同向率判断为0，
                # 那么有一些“与特定评论绑定”的词就会在下面的代码中被筛选出去，使准确率降低，这一点比较难理解
                # 比如有一个词只在这一条评论里出现了，那它得分一定与这条评论的label同向
                # 那么就很有助于模型反过来分析这个特定的数据集，因为这个词一定能正确影响这个评论的得分
                # 但是如果不准确赋值法训练了两次，前面的影响就不存在了，这个词会被保留下来，准确率也会提升
            else:
                word_siderate[word] = max(terms_side[word][0] / (terms_side[word][0] + terms_side[word][1]),
                                          terms_side[word][1] / (terms_side[word][0] + terms_side[word][1]))  #

for line in open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\car_opinions.csv', 'r',
                 encoding='UTF-8'):
    line = line.split(',')  # 分离label与review
    label = line[0]
    review = line[1].split(' ')  # 对review进行分词
    sentiment_score = 1
    if label == 'Neg':
        sentiment_score = -1
    for word in set(review):
        if len(word) >= terms_len and word_siderate[word] >= side_ratio \
                and (terms_side[word][0]+terms_side[word][1]) >= 1:
            # 此处的条件3可以说明，准确率存在虚高，一旦更换数据集，很多"片面之词"
            # （出现在某个评论里一次，与该评论绑定）都被算在其中，一旦抛开，准确率会大幅度降低
            sentiment_terms[word] = sentiment_terms.get(word, 0) + sentiment_score  #

print('side_ratio:', side_ratio, 'sentiment_terms count: ', len(sentiment_terms))

with open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\Training_terms.csv', 'w',
          encoding='UTF-8') as s_file:
    for sentiment in sentiment_terms:
        if abs(sentiment_terms[sentiment]) >= terms_occur:
            s_file.write(
                sentiment + ',' + str(sentiment_terms[sentiment]) + ',' + str(word_siderate[sentiment]) + '\n')
with open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\terms_side.csv', 'w',
          encoding='UTF-8') as s_file:
    for terms in terms_side:
        s_file.write(str(terms) + ',' + str(terms_side[terms][0])
                     + ',' + str(terms_side[terms][1]) + ',' + str(word_siderate[terms])
                     + '\n')
# 注意csv文件列间隔有 "," 作为间隔符
# Read sentiment terms

sentiment_terms = {}
for line in open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\Training_terms.csv',
                 encoding='UTF-8'):
    line = line.split(",")
    if len(line) == 3:
        sentiment_terms[line[0]] = float(line[1])

sentiment_list = []
for items in sentiment_terms:
    sentiment_list.append([items, sentiment_terms[items]])

sentiment_list.sort(key=lambda x: x[1])

sentiment_terms = {}
for i, item in enumerate(sentiment_list):
    sentiment_terms[item[0]] = 2 * i / len(sentiment_list) - 1  # 打分规范化 提高6%左右

total_accuracy = 0
total_review = 0
with open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\s_test.csv', 'w',
          encoding='UTF-8') as s_file:
    for line in open(r'C:\Users\Jianming\Desktop\技术栈\Courses in UCD\Programming for Analytics\car_opinions.csv',
                     encoding='UTF-8'):
        line = line.split(',')  # 分离label与review
        label = line[0]
        review = line[1].split(' ')  # 对review进行分词
        review_score = 0
        reviewed = {}
        for word in review:
            if word in sentiment_terms.keys() and word not in reviewed.keys():  # 0.767727 appear方法提高了一丁点
                review_score += sentiment_terms[word] * word_siderate[word]  # 添加权重
                reviewed[word] = 1
            # if word in sentiment_terms.keys():
            #     review_score += sentiment_terms[word]  # 0.767004
        s_file.write(str(review_score) + ',' + label + '\n')
        total_review += 1
        if review_score > 0 and label == 'Pos' or review_score < 0 and label == 'Neg':
            total_accuracy += 1

print('Terms_len: ', terms_len, 'Terms_occur: ', terms_occur)
print('Total_review', total_review)
print('Total_accuracy', total_accuracy)
print('Accuracy rate', total_accuracy / total_review)
