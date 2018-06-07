from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfEmbeddingVectorizer(object):
    """Get the ti-idf word2vec for each doc."""

    def __init__(self, word2vec):
        """Initialize the parameters.

        Parameters:
                    word2vec (object): the word2vec models
                    word2weight (dic): the dict {word: ti-idf}
                    dim (int): the dimensions
        """
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(word2vec.itervalues().next())

    def fit(self, X):
        """Get the model parameters from training set."""
        tfidf = TfidfVectorizer(analyzer=lambda x: x)
        tfidf.fit(X)
        max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(lambda: max_idf,
                                       [(w, tfidf.idf_[i]) for w, i in
                                        tfidf.vocabulary_.items()]
                                       )
        return self

    def transform(self, X):
        """Get the transformation for models.

        Parameters:
                    X (list): list of list of words.

        """
        return np.array([np.mean([self.word2vec[w] * self.word2weight[w]
                                  for w in words if w in self.word2vec] or
                                 [np.zeros(self.dim)], axis=0)
                         for words in X
                         ])
