"""
基于朴素贝叶斯公式实现垃圾邮件分类器
1.数据加载： 正确解析标签与文本，去除无效行（如文本为空）,邮件分为垃圾邮件和非垃圾邮件两类。
2.进行特征表示：使用词袋模型方法将文本转换为词频型特征向量，将垃圾邮件中出现频率较高的词作为特征。
4.分类：使用多项式朴素贝叶斯算法进行二分类，采用Laplace平滑处理，避免零概率问题。
5.模型评估：使用准确率、精确率、召回率和F1-score等指标评估模型性能，使用混淆矩阵分析分类结果。混淆矩阵使用行作为真实标签，列作为预测标签，展示分类结果的分布情况。
"""

import sklearn
import math
import re

class NaiveBayesClassifier:
    def __init__(self):
        self.vocabulary = set()  # 词汇表
        self.classifier = sklearn.naive_bayes.MultinomialNB(alpha=1.0)  # 多项式朴素贝叶斯分类器
        self.feature_vectorizer = None  # 在 fit() 中用有序词表创建向量化器

    def fit(self, X, y):
        # 构建词汇表
        for text in X:
            words = re.findall(r'\b\w+\b', text.lower()) #匹配所有单词，忽略标点符号和特殊字符
            self.vocabulary.update(words)

        # 将文本转换为词频特征向量
        vocab_list = sorted(self.vocabulary)
        self.feature_vectorizer = sklearn.feature_extraction.text.CountVectorizer(vocabulary=vocab_list)
        X_vectorized = self.feature_vectorizer.transform(X)
        # 训练分类器
        self.classifier.fit(X_vectorized, y)

    def predict(self, X):
        X_vectorized = self.feature_vectorizer.transform(X)
        return self.classifier.predict(X_vectorized)



if __name__ == "__main__":
    train_data_path = "train_set.csv"
    test_data_path = "test_set.csv"

    # 加载训练数据
    with open(train_data_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        X_train = []
        y_train = []
        for line in lines:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            label, text = line.split('\t', 1) 
            X_train.append(text)
            y_train.append(1 if label == 'spam' else 0)  #spam标签为1，ham标签为0
    
    # 加载测试数据
    with open(test_data_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        X_test = []
        y_test = []
        for line in lines:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            label, text = line.split('\t', 1) 
            X_test.append(text)
            y_test.append(1 if label == 'spam' else 0)  #spam标签为1，ham标签为0
    # 训练朴素贝叶斯分类器
    classifier = NaiveBayesClassifier()
    classifier.fit(X_train, y_train)
    # 预测测试数据
    y_pred = classifier.predict(X_test)
    # 评估模型性能
    accuracy = sklearn.metrics.accuracy_score(y_test, y_pred)
    precision = sklearn.metrics.precision_score(y_test, y_pred)
    recall = sklearn.metrics.recall_score(y_test, y_pred)
    f1_score = sklearn.metrics.f1_score(y_test, y_pred)
    confusion_matrix = sklearn.metrics.confusion_matrix(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1_score}")
    print("Confusion Matrix:")
    print(confusion_matrix)
