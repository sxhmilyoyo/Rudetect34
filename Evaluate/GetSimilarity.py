# import sys
# sys.path.append('..')
import os
from collections import defaultdict
from Clustering.MeanEmbeddingVectorizer import MeanEmbeddingVectorizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
from Clustering.TfidfEmbeddingVectorizer import TfidfEmbeddingVectorizer
# from Utility.Helper import Helper
# from Utility.PreprocessData import PreprocessData
import Utility


class GetSimilarity(object):
    """Use the K-means based on the word2vec features to cluster the tweets.

    The ways to get the word2vec for doc:
            MeanEmbeddingVectorizer: get the mean of word2vec for doc
            TfidfEmbeddingVectorizer: get the tf-idf of word2vec for doc2Label
    """

    def __init__(self, vectorizer, rootPath):
        """Initialize the parameters vectorizer.

        Options:
                mean (str): MeanEmbeddingVectorizer
                tfidf (str): TfidfEmbeddingVectorizer
        """
        if vectorizer == 'mean':
            self.vectorizer = MeanEmbeddingVectorizer
        elif vectorizer == 'tfidf':
            self.vectorizer = TfidfEmbeddingVectorizer
        else:
            print("Wrong vectorizer! Options: mean (str): " +
                  "MeanEmbeddingVectorizer; tfidf (str): " +
                  "TfidfEmbeddingVectorizer")
        self.rootPath = rootPath
        self.helper = Utility.Helper(rootPath)
        self.preprocessData = Utility.PreprocessData(rootPath)

    def getCosineSimilarity(self, corpus_vectors, target_vector):
        """Clsuter the tweet by using the k-means.

        Parameters:
                  folderPath (list): the path of the data folder
                  numClusters (int): the number of cluster

        """
        res = cosine_similarity(target_vector, corpus_vectors)
        return res

    def getCorpusFromCandidateStatements(self, folderPath):
        """Get svo from subject2svoqueries.json file.
        
        Arguments:
            folderPath {string} -- the path to data folder
        
        Returns:
            tuple -- (tokens, id2candiadateStatements)
        """
        candiadateStatements = self.preprocessData.getCandidateStatements(
            folderPath)
        id2candiadateStatements = dict(enumerate(candiadateStatements))
        tokens = []
        for candiadateStatement in candiadateStatements:
            token = self.preprocessData.getTokens(candiadateStatement)
            tokens.append(token)
        return tokens, id2candiadateStatements

    def getCorpusFromTargetStatements(self, folderPath):
        """Get target statements from target_statement.txt.
        
        Arguments:
            folderPath {str} -- the path to data folder
        
        Returns:
            list -- [token]
        """
        with open(os.path.join(self.rootPath, folderPath, 'final', 'target_statement.txt')) as fp:
            statement = fp.read()
        c1 = self.preprocessData.cleanTweet(statement)
        c2 = self.preprocessData.cleanTweet4Word2Vec(c1)
        token = self.preprocessData.getTokens(c2.lower())
        return [token]

    def getVector(self, corpus):
        model = self.helper.getWord2vec()
        w2v = {w: vec for w, vec in zip(model.wv.index2word, model.wv.syn0)}
        tfidf = self.vectorizer(w2v)
        tfidf.fit(corpus)
        tfidfX = tfidf.transform(corpus)
        return tfidfX

    def getCorpusFromTweets4Cluster(self, folderPath):
        """Get tweets in token format for clustering.
        
        Arguments:
            folderPath {str} -- the path to data folder
        
        Returns:
            tuple -- (tokens, id2tweets)
        """
        tweets = self.preprocessData.getTweetsFromTweetsLine(folderPath)
        id2tweets = dict(enumerate(tweets))
        tokens = []
        for tweet in tweets:
            token = self.preprocessData.getTokens(tweet)
            tokens.append(token)
        return tokens, id2tweets

    def getCorpusFromCandidateStatements4Cluster(self, folderPath):
        """Get candidate statements in token format for clustering.
        
        Arguments:
            folderPath {str} -- the path to folder
        
        Returns:
            tuple -- (tokens, id2candiadateStatements)
        """
        candiadateStatements = self.preprocessData.getCandidateStatements4Cluster(
            folderPath)
        id2candiadateStatements = dict(enumerate(candiadateStatements))
        tokens = []
        for candiadateStatement in candiadateStatements:
            token = self.preprocessData.getTokens(candiadateStatement)
            tokens.append(token)
        return tokens, id2candiadateStatements
