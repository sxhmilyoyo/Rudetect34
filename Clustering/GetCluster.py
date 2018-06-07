# import sys
# sys.path.append('..')
from collections import defaultdict
from .MeanEmbeddingVectorizer import MeanEmbeddingVectorizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from .TfidfEmbeddingVectorizer import TfidfEmbeddingVectorizer
# from Utility.Helper import Helper
# from Utility.PreprocessData import PreprocessData
import Utility


class GetCluster(object):
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
            print ("Wrong vectorizer! Options: mean (str): " +
                   "MeanEmbeddingVectorizer; tfidf (str): " +
                   "TfidfEmbeddingVectorizer")
        self.rootPath = rootPath
        self.helper = Utility.Helper(rootPath)
        self.preprocessData = Utility.PreprocessData(rootPath)

    def getKmeans(self, folderPath, numClusters):
        """Clsuter the tweet by using the k-means.

        Parameters:
                  folderPath (list): the path of the data folder
                  numClusters (int): the number of cluster

        """
        num_clusters = numClusters
        model = self.helper.getWord2vec()
        w2v = {w: vec for w, vec in zip(model.wv.index2word, model.wv.syn0)}

        # meanW2vTfidf = Pipeline([("word2vec vectorizer",
        #                           MeanEmbeddingVectorizer(w2v)),
        #                          ("k means", KMeans(n_clusters=num_clusters))])
        # kmeansW2vTfidf = Pipeline([("word2vec vectorizer",
        #                             TfidfEmbeddingVectorizer(w2v)),
        #                            ("k means", KMeans(n_clusters=num_clusters))])
        corpus = self.preprocessData.getCorpus(folderPath)
        tfidf = self.vectorizer(w2v)
        tfidf.fit(corpus)
        tfidfX = tfidf.transform(corpus)
        km = KMeans(n_clusters=num_clusters)
        km.fit(tfidfX)

        self.helper.dumpPickle(folderPath, 'kmeans.pkl', km)
        print ("km has been saved as kmeans.pkl file.")
        return km

    def getDoc2Label(self, folderPath, km):
        """Map the doc id to label id.

        Save the {doc: label} into 'doc2Label.json'.
        Parameters:
                    folderPath (list): the path of the data folder
                    km (Kmeans): the k-means object

        """
        d2l = defaultdict(int)
        for i in range(len(km.labels_)):
            d2l[i] = km.labels_[i]
        self.helper.dumpPickle(folderPath, 'doc2Label.pkl', d2l)

    def getLabel2Doc(self, folderPath, km):
        """Map the label id to doc id.

        Save the {label: [doc]} into the label2Doc.json.
        Parameters:
                    folderPath (list): the path of the data folder
                    km (Kmeans): the k-means object

        """
        l2d = defaultdict(list)
        for i in range(len(km.labels_)):
            l2d[km.labels_[i]].append(i)
        self.helper.dumpPickle(folderPath, 'label2Doc.pkl', l2d)
