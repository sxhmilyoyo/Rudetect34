import datetime
import tweepy
import Utility


class GetTwitterTrends(object):
    """Get Twitter Trends."""

    def __init__(self):
        """Initialize the parameters for Twitter API and API Handler."""
        consumerKey = "9wfdAl2hjbTLjWAoed5e6WbyT"
        consumerSecret = "GrS0HJc9oKi72mdlwHG73vNYoMKCRaYi1uB7Q5wpLA9c24Dxrl"
        accessToken = "3430332791-ROc4sJ99H5cPJIHD369WqI20PUvYQQdBLhlpPNs"
        accessTokenSecret = "8OQkqsbIpWdKq3xEQKdDXzukTjXwVske12B1pIWYDRK2g"

        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        self.api = tweepy.API(auth)

        self.helper = Utility.Helper()

    def getTrends(self, geoID=23424977):
        """Get Twitter Trends based on Yahoo! Where On Earth ID.

        Save the json files on local.
        Args:
            geoID (int): the Yahoo! Where On Earth ID, the defailt USA is
                         23424977
        Returns:E
            None
        """
        trends = self.api.trends_place(geoID)
        self.helper.dumpJson("trends", str(datetime.date.today()) + ".json",
                             trends)
