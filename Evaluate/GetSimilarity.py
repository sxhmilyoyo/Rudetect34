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

    def getCorpusOfCandidateClaims(self, folderPath):
        """Get corpus of candidate claims.

        Arguments:
            folderPath {string} -- the path to data folder

        Returns:
            tuple -- (tokens, id2claims)
        """
        claims = self.preprocessData.getCandidateClaims(
            folderPath)

        id2claims = dict(enumerate(claims))
        self.helper.dumpJson(os.path.join(folderPath, "final"),
                             "id2claims_total.json", id2claims)
        print("id2claims_total.json has been saved.")
        tokens = []
        for claim in claims:
            token = self.preprocessData.getTokens(claim)
            tokens.append(token)
        return tokens, id2claims

    def getCorpusOfTargetClaim(self, folderPath):
        """Get corpus of target claim from target_statement.txt.

        Arguments:
            folderPath {str} -- the path to data folder

        Returns:
            list -- [token]
        """
        with open(os.path.join(self.rootPath, folderPath, 'target_statement.txt')) as fp:
            statement = fp.read()
        c1 = self.preprocessData.cleanTweet(statement)
        token = self.preprocessData.getTokens(c1.lower())
        return [token]

    def getVector(self, corpus):
        model = self.helper.getWord2vec()
        w2v = {w: vec for w, vec in zip(model.wv.index2word, model.wv.syn0)}
        tfidf = self.vectorizer(w2v)
        tfidf.fit(corpus)
        tfidfX = tfidf.transform(corpus)
        return tfidfX

    def getCorpusOfTweets(self, folderPath):
        """Get tweets in token format for clustering.

        Arguments:
            folderPath {str} -- the path to data folder

        Returns:
            tuple -- (tokens, id2tweets)
        """
        tweets = list(self.helper.getTweet(folderPath))
        id2tweets = dict(enumerate(tweets))
        self.helper.dumpJson(os.path.join(folderPath, "final"), "id2tweets_total.json", id2tweets)
        print("id2tweets_total.json has been saved.")
        tokens = []
        for tweet in tweets:
            token = self.preprocessData.getTokens(tweet)
            tokens.append(token)
        return tokens, id2tweets

    # def getCorpusFromCandidateStatements4Cluster(self, folderPath):
    #     """Get corpus of candidate statements in token format for clustering.

    #     Arguments:
    #         folderPath {str} -- the path to folder

    #     Returns:
    #         tuple -- (tokens, id2candiadateStatements)
    #     """
    #     candiadateStatements = self.preprocessData.getCandidateStatements4Cluster(
    #         folderPath)
    #     id2candiadateStatements = dict(enumerate(candiadateStatements))
    #     tokens = []
    #     for candiadateStatement in candiadateStatements:
    #         token = self.preprocessData.getTokens(candiadateStatement)
    #         tokens.append(token)
    #     return tokens, id2candiadateStatements
