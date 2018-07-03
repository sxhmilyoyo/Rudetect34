import codecs
import csv
from gensim.models.word2vec import Word2Vec
import json
import networkx
from networkx.algorithms.components.connected import connected_components
import numpy as np
import operator
import os
import pickle
import scipy
import sys
sys.path.append('/usa/haoxu/Workplace/InfoLab/RuDetect27/GetOldTweets-python')
import got3
import Twitter
import Utility


class Helper(object):
    """Implement some utility functions.

    loadPickle(filePath): load .pkl
    dumpPickle(fileFolderPath, filename, data): dump .pkl
    loadJson(filePath): load .josn
    dumpJson(fileFolderPath, filename, data): dump .json
    """

    def __init__(self, rootPath):
        """Initialize the parameters.

        self.rootPath: the path of data.
        """
        self.rootPath = rootPath
        # "/local/data/haoxu/Rudetect"

    def loadPickle(self, filePath):
        """Load .pkl."""
        # with codecs.open(os.path.join(self.rootPath, filePath), "rb",encoding='utf-8', errors='ignore') as fp:
        if not os.path.exists(os.path.join(self.rootPath, filePath)):
            return None
        with open(os.path.join(self.rootPath, filePath), 'rb') as fp:
            data = pickle.load(fp)
        return data

    def dumpPickle(self, fileFolderPath, filename, data):
        """Dump .pkl."""
        if not os.path.exists(os.path.join(self.rootPath, fileFolderPath)):
            os.makedirs(os.path.join(self.rootPath, fileFolderPath))
        with open(os.path.join(self.rootPath, fileFolderPath, filename),
                  "wb") as fp:
            pickle.dump(data, fp)

    def loadJson(self, filePath):
        """Load .json."""
        if not os.path.exists(os.path.join(self.rootPath, filePath)):
            return None
        with open(os.path.join(self.rootPath, filePath)) as fp:
            data = json.load(fp)
        return data

    def dumpJson(self, fileFolderPath, filename, data):
        """Dump .pkl."""
        if not os.path.exists(os.path.join(self.rootPath, fileFolderPath)):
            os.makedirs(os.path.join(self.rootPath, fileFolderPath))
        with open(os.path.join(self.rootPath, fileFolderPath, filename),
                  "w") as fp:
            json.dump(data, fp, indent=4)

    def dumpCsv(self, folderPath, filename, title, data):
        """Short summary.

        Parameters
        ----------
        folderPath : str
            event folder path.
        filename : str
            file name.
        title : list
            ['t1', 't2', ...].
        data : list
            [d1, d2, ...].

        Returns
        -------
        type
            Description of returned object.

        """
        if not os.path.exists(os.path.join(self.rootPath, folderPath)):
            os.makedirs(os.path.join(self.rootPath, folderPath))
        with open(os.path.join(self.rootPath, folderPath, filename), "w") as fp:
            filewriter = csv.writer(fp, delimiter='\t')
            filewriter.writerow(title)
            for d in data:
                filewriter.writerow(d)
        print("{} has been saved in {}".format(
            filename, os.path.join(self.rootPath, folderPath, filename)))

    def loadCsv(self, folderPath, filename):
        details = []
        if not os.path.exists(os.path.join(self.rootPath, folderPath, filename)):
            return None
        with open(os.path.join(self.rootPath, folderPath, filename)) as fp:
            reader = csv.reader(fp, delimiter='\t')
            next(reader)
            for r in reader:
                details.append(r)
        return details

    def getTweet(self, folderPath):
        """Get tweet content from tweet object.

        It is a generator.
        Parameters Example:
                self.rootPath/folderPath/final/rawData
        """
        filenames = os.listdir(os.path.join(self.rootPath, folderPath,
                                            'final', 'rawData'))
        for filename in filenames:
            tweets = self.loadPickle(os.path.join(folderPath, 'final',
                                                  'rawData', filename))
            for tweet in tweets:
                yield tweet

    def getClaim(self, folderPath, filename):
        """Get claim content from subject2rankedClaims.json.

        Arguments:
            folderPath {str} -- the path to folder that contains file of claim
            filename {str} -- the filename of the claim.
        """
        subject2claims = self.loadJson(os.path.join(folderPath, 'final',
                                                    filename))
        for subject in subject2claims:
            for tweetID, claim in subject2claims[subject]:
                yield claim

    def getWord2vec(self):
        """Get the word2vec model.

        Parameters Example:
                self.rootPath/folderPath/w2model

        """
        return Word2Vec.load(os.path.join(self.rootPath, 'w2vmodel'
                                          ))

    def mergeOverlappedList(self, data):
        """Merge the overlapped list of intervals.

        Parameters
        ----------
        data : list
            format: [[x1, x2], [x3, x4], ...]

        Returns
        -------
        list
            the merged list of intervals
            format is same as data's

        """
        data = sorted(data, key=operator.itemgetter(0))
        n = len(data)
        stack = [data[0]]
        for i in xrange(1, n):
            if stack[-1][1] < data[i][0]:
                stack.append(data[i])
            else:
                top = (stack[-1][0], data[i][1])
                stack.pop()
                stack.append(top)
        return stack

    def getTopicNum(self, dist):
        """Get the topic number for k-means.

        Use the KL-Divergence to Calculate the similarity between
        any two topic word distributions and merge the topics which
        KL-Divergence are small than the (mean - sd)
        Parameters
        ----------
        dist : numpy.array
            the array of topic word distributions

        Returns
        -------
        int
            the number of the topic for k-means

        """
        n = len(dist)
        kld = {}
        for i in xrange(n):
            for j in xrange(i + 1, n):
                kld[(i, j)] = scipy.stats.entropy(dist[i], dist[j])
        klds = kld.values()
        try:
            mean = sum(klds) / float(len(klds))
        except Exception as e:
            print(e)
            mean = 0
        try:
            sd = np.std(klds, ddof=1)
        except Exception as e:
            print(e)
            sd = 0
        # list of similar topic id
        similarTopic = [k for k in kld if kld[k] <= mean - sd]
        print("the similar topic is {}".format(similarTopic))
        # list remained of topic id
        remainTopic = []
        for tp in xrange(n):
            flag = False
            for t in similarTopic:
                if tp in t:
                    flag = True
                    break
            if not flag:
                remainTopic.append(tp)
        print("the remained topic is {}".format(remainTopic))
        if similarTopic:
            mergedSimilarTopic = self.getConnectedComponents(similarTopic)
            print("the merged similar topic is {}".format(mergedSimilarTopic))
            # topicNum = len(dist) - len(similarTopic) + len(mergedSimilarTopic)
            topicNum = len(mergedSimilarTopic) + len(remainTopic)
        else:
            topicNum = len(dist)
        return topicNum

    def chunkify(self, _list, chunk_size):
        """Split the original data into chunks.

        Parameters
        ----------
        _list : list
            a list of data
        chunk_size : int
            the size of chunk

        Returns
        -------
        generator
            iteratively generate the chunk

        """
        for i in xrange(0, len(_list), chunk_size):
            yield _list[i: i + chunk_size]

    def getHistoricalTweets(self, username, foldername):
        """Get the historical tweets of user.

        Parameters
        ----------
        username : str
            the username of account without '@'

        Returns
        -------
        None
            save the tweet object in username.pkl file

        """
        tweetFlag = True
        getTwitterData = Twitter.GetTwitterData(self.rootPath)
        criteria = getTwitterData.setCriteria(username=username)
        getTwitterData.getTweets(criteria, foldername,
                                 username + ".pkl", tweetFlag)

    @classmethod
    def to_graph(cls, groupNodes):
        """Generate graph based on groupNodes.

        Parameters
        ----------
        groupNodes : list
            list of list of nodes

        Returns
        -------
        networkx.classes.graph.Graph
            graph object

        """
        G = networkx.Graph()
        for groupNode in groupNodes:
            G.add_nodes_from(groupNode)
            G.add_edges_from(cls.to_edges(groupNode))
        return G

    @classmethod
    def to_edges(cls, groupNode):
        """Generate edge between neighbor points.

        Parameters
        ----------
        groupNode : list
            list of nodes

        Returns
        -------
        generator
            tuple of neighbor points

        """
        it = iter(groupNode)
        last = next(it)

        for current in it:
            yield last, current
            last = current

    @classmethod
    def getConnectedComponents(cls, groupNodes):
        """Get connected components from group of nodes.

        Parameters
        ----------
        groupNodes : list
            list of list of points

        Returns
        -------
        list
            list of connected components

        """
        G = cls.to_graph(groupNodes)
        return list(connected_components(G))
