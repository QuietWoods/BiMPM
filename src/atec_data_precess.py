# -*- coding: utf-8 -*-
# @Time    : 2018/6/28 9:59
# @Author  : QuietWoods
# @FileName: atec_data_precess.py
# @Software: PyCharm
# @Email    ：1258481281@qq.com
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import jieba.posseg as pseg

jieba.load_userdict('mydict/mydict.txt')
STOP_DICT = 'mydict/stopdict.txt'


class AtecCorpus(object):
    def __init__(self):
        pass

    def merge_file(self, file1, file2, file3):
        """
        合并文件
        :param file1:
        :param file2:
        :param file3:
        :return:
        """
        merge = open(file3, 'w')
        with open(file1, 'r') as fin:
            for line in fin:
                if line.strip():
                    merge.write(line)
        with open(file2, 'r') as fin:
            for line in fin:
                if line.strip():
                    merge.write(line)
        merge.close()
        print('******************{} + {} ---> {} have Done!***********'.format(file1, file2, file3))

    def split_pos_neg(self, inpath):
        """
        切分语料中的正负类
        :param fin:
        :return:
        """
        pos_file = 'data/atec_nlp_sim_train_pos.csv'
        neg_file = 'data/atec_nlp_sim_train_neg.csv'
        with open(inpath, 'r') as fin, open(pos_file, 'w') as pos_out, open(neg_file, 'w') as neg_out:
            for line in fin:
                lineno, sent1, sent2, label = line.strip().split('\t')
                if label == '0':
                    neg_out.write(line)
                elif label == '1':
                    pos_out.write(line)
                else:
                    print(line)
        print('******************{}---> {} + {} have Done!***********'.format(inpath, pos_file, neg_file))

    def segment_clear_text(self, inpath, outpath):
        """
        分词，替换，清洗语料
        :param fin:
        :param fout:
        :return:
        """
        before = [0] * 60
        after = [0] * 60
        with open(inpath, 'r') as fin, open(outpath, 'w') as fout:
            for line in fin:
                lineno, sent1, sent2, label = line.strip().decode('utf-8').split('\t')
                words1 = self.segment_clear_sentence(sent1)
                words2 = self.segment_clear_sentence(sent2)
                if len(words1) >= 60:
                    after[59] += 1
                else:
                    after[len(words1)] += 1
                if len(words2) >= 60:
                    after[59] += 1
                else: 
                    after[len(words2)] += 1
                if len(sent1) >= 60:
                    before[59] += 1
                else:
                    before[len(sent1)] += 1
                if len(sent2) >= 60:
                    before[59] += 1
                else:
                    before[len(sent2)] += 1
                # print('-----------------------')
                # print(label)
                # print(sent1.encode('utf-8'))
                # print(' '.join(words1).encode('utf-8'))
                # print(sent2.encode('utf-8'))
                # print(' '.join(words2).encode('utf-8'))
                # print('-----------------------')
                fout.write(' '.join(words1).encode('utf-8') + '\n')
                fout.write(' '.join(words2).encode('utf-8') + '\n')
        print('******************{}-->{}'.format(inpath, outpath))
        x_axis = [i for i in range(60)]
        plt.plot(x_axis, before, 'k--', label='before len')
        plt.plot(x_axis, after, 'r-', label='after len')
        plt.title('sentence length')
        plt.xlabel('length')
        plt.ylabel('sentences number')
        plt.legend(loc='upper left')
        plt.savefig('sentences length.png')

    def stop_list(self):
        """
        停用词表
        :return: 返回停用词列表
        """
        stop_list = []
        with open(STOP_DICT, 'r') as fin:
            for line in fin:
                word = line.strip().decode('utf-8')
                stop_list.append(word)
        return stop_list

    def segment_clear_sentence(self, sentence, POS_FLAG=False):
        """
        分词，替换，清洗句子
        :param sentence: 字符串列表
        :return: 字符串列表
        """
        sent = sentence.strip()
        if sent:
            sent = self.string_re(sent)
            stop_dict = self.stop_list()
            if POS_FLAG:
                words = pseg.cut(sent)
                # 添加词性，去空白字符，停用词
                return [w.word + "/" + w.flag for w in words if w.word.strip() and w.word not in stop_dict]
            else:
                words = jieba.cut(sent)
                return [w for w in words if w.strip() and w not in stop_dict]
        else:
            return None

    def string_re(self, sent):
        """
        替换语料中一些不规范的符号和词
        :param sent:
        :return:
        """
        # sent = sent.decode('utf-8')
        if sent[-2:] == u'怎样':
            sent = sent[:-2] + u'怎么样'
        if sent[-1] in [u'不', u'嘛', u'么']:
            sent = sent[:-1] + u'吗'
        # ****替换成 几
        sent = re.sub(r'\d*\*+\d*', u'几', sent)
        sent = re.sub(u'唄', u'呗', sent)
        sent = re.sub(u'開', u'开', sent)
        sent = re.sub(u'螞蟻', u'蚂蚁', sent)
        sent = re.sub(u'証', u'证', sent)
        sent = re.sub(u'還', u'还', sent)
        sent = re.sub(u'qb', u'Q币', sent)
        sent = re.sub(u'咋|啥', u'怎么', sent)
        sent = re.sub(u'花贝', u'花呗', sent)
        sent = re.sub(u'借贝', u'借呗', sent)
        sent = re.sub(u'蚂蚁借呗', u'借呗', sent)
        sent = re.sub(u'蚂蚁花呗', u'花呗', sent)
        return sent

def test_string_re():
    tt = AtecCorpus()
    # test *****************************
    test1 = u'我的花呗退款余额在那去了啥,我支付宝里花呗余额显示没有咋	蚂蚁花贝不小心按差了 在*** 点了退票 123***345显示123***退票成功 为什么支付宝花呗没有显示嘛怎样'
    r_tt1 = tt.string_re(test1)
    w_tt1 = u'我的花呗退款余额在那去了怎么,我支付宝里花呗余额显示没有怎么	花呗不小心按差了 在几 点了退票 几显示几退票成功 为什么支付宝花呗没有显示嘛怎么样'
    print('1')
    if r_tt1 == w_tt1:
        print(u'啥， 咋， ****， 123***123， 123****， 怎样， pass')
    else:
        print(test1)
        print(r_tt1)
        print('failed')

    test1 = u'我的蚂蚁花呗退款余额在那去了啥,我支付宝里花呗余额显示没有咋借贝	蚂蚁花贝不小心按差了 在*** 点了退票 123***345显示123***退票成功 为什么支付宝花呗没有显示嘛'
    r_tt1 = tt.string_re(test1)
    w_tt1 = u'我的花呗退款余额在那去了怎么,我支付宝里花呗余额显示没有怎么借呗	花呗不小心按差了 在几 点了退票 几显示几退票成功 为什么支付宝花呗没有显示吗'
    print('2')
    if r_tt1 == w_tt1:
        print(u'蚂蚁花呗， 借贝，嘛 ， pass')
    else:
        print(test1)
        print(r_tt1)
        print('failed')

def main():
    # 1.合并两次的语料
    atec = AtecCorpus()
    file1 = 'data/atec_nlp_sim_train.csv'
    file2 = 'data/atec_nlp_sim_train_add.csv'
    mergefile = 'data/atec_nlp_sim_train_merge.csv'
    atec.merge_file(file1, file2, mergefile)
    # 2.切分正负类
    atec.split_pos_neg(mergefile)
    # 3.分词，清洗
    atec.segment_clear_text(mergefile, 'data/atec_nlp_sim_train_corous.csv')


if __name__ == '__main__':
    # test_string_re()
    main()


