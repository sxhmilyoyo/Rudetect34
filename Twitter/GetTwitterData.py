# import sys
# sys.path.append('../GetOldTweets-python')
# sys.path.append('..')
import got3
# from Utility.Helper import Helper
import Utility


class GetTwitterData(object):
    """Use GetOldTweets-python to crawl the Twitter data."""

    def __init__(self, rootPath):
        """Initialize the Parameters.

        Parameters:
            criteria (object): the criteria object for got module
            manager (object): the manager object for got module
            helper (object): the helper object for Utility.Helper module

        """
        self.criteria = got3.manager.TweetCriteria()
        self.manager = got3.manager.TweetManager()
        self.helper = Utility.Helper(rootPath)

    def setCriteria(self, query=None, start=None, end=None, maxTweets=None, username=None):
        """Set the criteria for twitter crawler.

        Parameters:
            query (str): the query string
            start (str): the start date yyyy-mm-dd
            end (str): the end date yyyy-mm-dd
            maxTweets (int): the number of max tweet needed
        Returns:
            object: criteria for twitter crawler used

        """
        if username:
            criteria = self.criteria.setUsername(username)
        else:
            criteria = self.criteria.setQuerySearch(query).setSince(
                start).setUntil(end).setMaxTweets(maxTweets)
        return criteria

    def getTweets(self, criteria, folderPath, filename):
        """Get tweets.

        The crawled tweets saved as filename.
        Parameters:
            criteria (object): the criteria object for twitter crawler
            folderPath (str): the folder path
            filename (str): the filename
            Example: self.root/folderPath/filename
        Returns:
            None

        """
        tweets, totalNumTweets = self.manager.getTweets(criteria)
        self.helper.dumpPickle(folderPath, filename, tweets)
        print ("{} has been saved with total {} tweets.".format(filename,
                                                                len(tweets)))
        return totalNumTweets

    # def addressTweet(self, tweets, filename):
    # 	self.helper.dumpPickle('NYCattack', filename, tweets)
