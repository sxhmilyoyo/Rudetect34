import time
from datetime import datetime


class Tweet(object):
    """Tweet object"""
    id = None
    text = None
    favorites = None
    retweets = None
    hashtags = None
    date = None
    reply = None
    rumor = None

    def setHashtags(self, hashtags):
        """Set hashtags attributes of tweet.

        Arguments:
            hashtags {list} -- a list of hashtags
        """
        self.hashtags = ' '.join(hashtags)

    def setDate(self, date):
        """Set date attribute of tweetself.

        Arguments:
            date {str} -- a string of date
        """
        timeStruct = time.strptime(date, "%a %b %d %H:%M:%S +0000 %Y")
        self.date = datetime.fromtimestamp(time.mktime(timeStruct))
