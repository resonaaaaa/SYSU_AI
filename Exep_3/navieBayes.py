import sklearn
import math
import re

class NaiveBayes:
    pass

class MultinomialNB(NaiveBayes):
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        self.classes_ = set(y)
        self.class_count_ = {c: 0 for c in self.classes_}  
        self.feature_count_ = {c: {} for c in self.classes_}  
        self.feature_log_prob_ = {c: {} for c in self.classes_}

        for xi, yi in zip(X, y):
            self.class_count_[yi] += 1
            for feature in xi:
                if feature not in self.feature_count_[yi]:
                    self.feature_count_[yi][feature] = 0
                self.feature_count_[yi][feature] += 1

        for c in self.classes_:
            total_count = sum(self.feature_count_[c].values()) + self.alpha * len(self.feature_count_[c])
            for feature in self.feature_count_[c]:
                count = self.feature_count_[c][feature] + self.alpha
                self.feature_log_prob_[c][feature] = math.log(count / total_count)

    def predict(self, X):
        predictions = []
        for xi in X:
            class_scores = {c: math.log(self.class_count_[c] / sum(self.class_count_.values())) for c in self.classes_}
            for feature in xi:
                for c in self.classes_:
                    if feature in self.feature_log_prob_[c]:
                        class_scores[c] += self.feature_log_prob_[c][feature]
            predicted_class = max(class_scores, key=class_scores.get)
            predictions.append(predicted_class)
        return predictions
    
class BagOfWords:
    def __init__(self):
        self.vocabulary = set()

    def fit(self, X):
        for document in X:
            words = re.findall(r'\b\w+\b', document.lower())
            self.vocabulary.update(words)

    def transform(self, X):
        sklearn.count_vectorizer = sklearn.feature_extraction.text.CountVectorizer(vocabulary=self.vocabulary)
        return sklearn.count_vectorizer.transform(X)
    
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)
    