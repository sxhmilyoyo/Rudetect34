class Tweet(object):
    """Tweet object"""
    def __init__(self, id, text, favorite_count, retweet_count, comment, rumor):
        self.id = id
        self.text = text
        self.favorite_count = favorite_count
        self.retweet_count = retweet_count
        self.comment = comment
        self.rumor = rumor
        