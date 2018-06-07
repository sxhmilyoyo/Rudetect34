import numpy as np


class MeanEmbeddingVectorizer(object):
    """Get the mean word2vec."""

    def __init__(self, word2vec):
        """Initialize the word2vec and vector's dimensions."""
        self.word2vec = word2vec
        self.dim = len(word2vec.itervalues().next())

    def fit(self, X, y):
        """Learn model parameters from a training set."""
        return self

    def transform(self, X):
        """Apply the transformation model to unseen model."""
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])
