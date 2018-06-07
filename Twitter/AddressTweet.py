# import sys
# sys.path.append('../GetOldTweets-python')
import got3
# sys.path.append('..')
from collections import defaultdict
from fuzzywuzzy import fuzz
# from Utility.Helper import Helper
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import operator
import os
import Utility


class AddressTweet(object):
    """Address the tweet.

    Methods:
        getHashtags(filePath)
        getUserName(filePath)
        sortDict(d)
        getTop10(self, d, sortedDict)
        getStatistics(self, d)
        getPlot(self, sorted_d, filePath, filename, flag_percent)
        getSortedHashTags(self, hashtags)

    """

    def __init__(self, rootPath):
        """Initialize the parameters.

        Args:
            rootPath (str): the root path of the data.
            helper (instance): the instance of the Helper() object.
        """
        self.rootPath = rootPath
        self.helper = Utility.Helper(self.rootPath)

    def getHashtags(self, filePath, query):
        """Get hashtags from tweet object and save it in .pkl file.

        Save the hashtags(dict) into hashTags.pkl
        Save the sorted hashtags(tuple) into sortedHashTags.pkl
        Save the top10 hashtags(dict) into top10HashTags.pkl
        Save the plot of top10 hashtags into top10HashTags.png
        Args:
            filePath (str): the path of the file that contains tweet objects.
            Example: self.rootPath/filePath/rawData
        Returns:
            None

        """
        filenames = os.listdir(os.path.join(self.rootPath, filePath,
                                            'rawData'))
        hashTags = defaultdict(int)
        for filename in filenames:
            tweets = self.helper.loadPickle(os.path.join(filePath,
                                                         'rawData', filename))
            for tweet in tweets:
                hashTaglist = tweet.hashtags.split()
                for hashTag in hashTaglist:
                    hashTags[hashTag] += 1
        s = self.getSimilarHashTags(query, list(hashTags))
        print(s)

        sortedHashTags = self.sortDict(hashTags)
        top10HashTags = self.getTop10(hashTags, sortedHashTags)
        top10 = set([key for key in top10HashTags.keys()])
        for h in s.keys():
            if h in top10:
                continue
            top10HashTags[h] = (0, 0)

        self.helper.dumpPickle(filePath, "hashTags.pkl", hashTags)
        print ("hashTags.pkl has been saved.")
        self.helper.dumpPickle(filePath, "sortedHashTags.pkl", sortedHashTags)
        print ("sortedHashTags.pkl has been saved.")
        self.helper.dumpPickle(filePath, "top10HashTags.pkl", top10HashTags)
        print ("top10HashTags.pkl has been saved.")
        averageHashTags = self.getStatistics(hashTags)
        print ("Average number of hashtag is {}".format(averageHashTags))
        self.getPlot(top10HashTags, filePath, "top10HashTags.png", True)
        print ("top10HashTags.pkl has been saved.")

    def getUserName(self, filePath):
        """Get username from tweet objects and save it in .pkl file.

        Save the userName(dict) into hashTags.pkl
        Save the sorted userName(tuple) into sortedHashTags.pkl
        Save the top10 userName(dict) into top10HashTags.pkl
        Save the plot of top10 userName into top10HashTags.png
        Args:
            filePath (str): the path of the file that contains tweet objects.
        Returns:
            None

        """
        filenames = os.listdir(os.path.join(self.rootPath, filePath,
                                            'rawData'))
        userName = defaultdict(int)
        for filename in filenames:
            tweets = self.helper.loadPickle(os.path.join(filePath, 'rawData',
                                                         filename))
            for tweet in tweets:
                userName[tweet.username] += 1
        sortedUserName = self.sortDict(userName)
        top10UserName = self.getTop10(userName, sortedUserName)
        self.helper.dumpPickle(filePath, "userName.pkl", userName)
        print ("userName.pkl has been saved.")
        self.helper.dumpPickle(filePath, "sortedUserName.pkl", sortedUserName)
        print ("sortedUserName.pkl has been saved.")
        self.helper.dumpPickle(filePath, "top10UserName.pkl", top10UserName)
        print ("top10UserName.pkl has been saved.")
        averageUserName = self.getStatistics(userName)
        print ("Average tweet for each tweeter is {}".format(averageUserName))
        self.getPlot(top10UserName, filePath, "top10UserName.png", False)
        print ("top10UserName.pkl has been saved.")

    def sortDict(self, d):
        """Sort the dictionary.

        Args:
            d (dict): the dictionary
        Returns:
            list: sorted_dict
        """
        sorted_dict = sorted(d.items(), key=operator.itemgetter(1),
                             reverse=True)
        return sorted_dict

    def getTop10(self, d, sortedDict):
        """Get top10 hashtags from tweet objects.

        Args:
            d (dict): the dictionary {hashtag: number}
            sortedDict (list): the sorted dictionary [(hashtag, number)]
        Returns:
            dict: top10

        """
        numValue = sum(d.values())
        top10 = defaultdict(tuple)
        if len(sortedDict) < 10:
            length = len(sortedDict)
        else:
            length = 10
        for i in range(length):
            top10[sortedDict[i][0]] = (sortedDict[i][1] / float(numValue) * 100,
                                       sortedDict[i][1])
        return top10

    def getStatistics(self, d):
        """Get the statistics based on the data.

        Args:
            d (dict): the dictionary of the dataPath
        Returns:
            float: average
        """
        numValue = sum(d.values())
        numKey = len(d.keys())
        average = numValue / float(numKey)
        return average

    def getPlot(self, sorted_d, filePath, filename, flag_percent):
        """Get the plot based on the statistics.

        Args:
            sorted_d (list): the list of the information
            filePath (str): the path of the data
            filename (str): the name of the file
            flag_percent (boolean): indicate percentage or not
        Returns:
            None
        """
        x = [i for i in range(len(sorted_d))]
        if flag_percent is True:
            y = [i[0] for i in sorted_d.values()]
        else:
            y = [i[1] for i in sorted_d.values()]
        plt.bar(x, y)
        plt.xticks(x, [i for i in sorted_d.keys()])
        plt.setp(plt.gca().get_xticklabels(), rotation=45,
                 horizontalalignment='right')
        plt.savefig(os.path.join(self.rootPath, filePath, filename),
                    bbox_inches='tight')
        plt.clf()

    def recordTweetNum(self, folderPath, query, totalNumTweets):
        """Record the number of tweet with the query.

        Save the {query: num} as the tweetNum.json file.
        Parameters:
            query (str): the query
            totalNumTweets (int): the number of tweets
        Returns:
            None

        """
        if os.path.isfile(os.path.join(self.rootPath, folderPath,
                          'tweetNum.json')):
            tweetNum = self.helper.loadJson(folderPath + '/tweetNum.json')
        else:
            tweetNum = {}
        tweetNum[query] = totalNumTweets
        self.helper.dumpJson(folderPath, 'tweetNum.json', tweetNum)

    def getSimilarHashTags(self, originHashtag, hashtags):
        """Get similar hashtags w.r.t. the original hashtags.
    
        Args:
            hashtags (list): a list of hashtags from the tweets
            orignHashtags (str): the initial hashtag
        Returns:
            list: similarHashTags
        """
        hashtag2score = {}
        for hashtag in hashtags:
            if originHashtag == hashtag:
                continue
            simScore = max(fuzz.token_set_ratio(originHashtag, hashtag),
                           fuzz.partial_ratio(originHashtag, hashtag) if
                           len(originHashtag) < len(hashtag) else 0)
            hashtag2score[hashtag] = simScore
        # average = sum(temp.values()) / float(len(temp.keys()))
        # print ("hashtag2score is {}".format(self.sortDict(hashtag2score)))
        res = {h: hashtag2score[h] for h in hashtag2score if hashtag2score[h]
               >= 90}
        # print ("new hashtags are: {}".format(res))
        return res
    #
    # def getFinalTop10HashTags(self, similarHashTags, hashtags):
    #     """Get the top10 hashtags based on the formula: times.
    #
    #     Args:
    #         similarHashTags (dict): the dictionary of hashtags with similar
    #                                 scores
    #         hashtags (dict): the dictionary of hashtags with number
    #     Returns:
    #         list: finalTop10HashTags
    #     """
    #     temp = {}
    #     for hashtag in similarHashTags.keys():
    #         s = similarHashTags[hashtag] * hashtags[hashtag]
    #         temp[hashtag] = s
    #     sortedTemp = self.sortDict(temp)
    #     if len(sortedTemp) >= 10:
    #         res = sortedTemp[:10]
    #     else:
    #         res = sortedTemp[:]
    #     print ("new hashtags {}".format(res))
    #     return [r[0] for r in res]

    # def getHashTags(self, filePath):
    #     """Get the hashtags from tweet objects.
    #
    #     Args:
    #         filePath (str): the path of the files
    #     Returns:
    #         dict: hashTags2num
    #     """
    #     tweets = self.helper.loadPickle(filePath)
    #     hashTags2num = defaultdict(int)
    #     for tweet in tweets:
    #         hashTags2num[tweet.hashtags.lower()] += 1
    #     return hashTags2num

    # def getSortedHashTags(self, hashtags):
    #     """Get the sorted hashtags.
    #
    #     Args:
    #         hashtags (d): the dictionary of the hashtags
    #     Returns:
    #         None
    #     """
    #     # test 20 hashtags
    #     sortedHashTags = sorted(hashtags.items(), key=operator.itemgetter(1),
    #                             reverse=True)
    #     self.helper.dumpPickle("Texas Shooting/4", "TotalHashtags_test.pkl",
    #                            sortedHashTags)
    #     return sortedHashTags
