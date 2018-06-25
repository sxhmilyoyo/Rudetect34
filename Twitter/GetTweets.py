# import sys
# sys.path.append('..')
# import click
# from fuzzywuzzy import fuzz
import os
import Twitter
import Utility


class GetTweets(object):
    """Get the final tweets after addressing the queries."""

    def __init__(self, rootpath, folderpath, start, end, originhashtag):
        """Initialize the parameters.

        Parameters
        ----------
        rootpath : str
            the root path of the data
        folderpath : str
            the folder path of the data
        start : str
            the start date of the query
            format: 'yyyy-mm-dd'
        end : str
            the end date of the query
            format: 'yyyy-mm-dd'
        originhashtag : str
            the original query hashtag

        Returns
        -------
        None

        """
        self.rootpath = rootpath
        self.folderpath = folderpath
        self.start = start
        self.end = end
        self.filename = "tweets.pkl"
        self.originhashtag = originhashtag
        self.helper = Utility.Helper(rootpath)
        self.addressTweet = Twitter.AddressTweet(rootpath)
        self.getTwitter = Twitter.GetTwitterData(rootpath)

    def get_address_twitter(self, query, folderPath, maxTweets):
        """Get and address tweets."""
        print("start crawling from {} to {} with file {}".format(self.start,
                                                                 self.end,
                                                                 os.path.join
                                                                 (folderPath,
                                                                  self.filename)))
        criteria = self.getTwitter.setCriteria(query, self.start, self.end,
                                               maxTweets)
        # print (criteria)
        print("crawling tweets...")
        totalNumTweets = self.getTwitter.getTweets(criteria,
                                                   os.path.join(folderPath,
                                                                'rawData'),
                                                   self.filename)

        print("recording the number of tweets...")
        self.addressTweet.recordTweetNum(folderPath, query, totalNumTweets)
        # address tweets
        print("get hashtags...")
        self.addressTweet.getHashtags(folderPath, query)
        print("get userIdName...")
        self.addressTweet.getUserName(folderPath)

        top10HashTags = self.helper.loadPickle(os.path.join(folderPath,
                                                            "top10HashTags.pkl"
                                                            ))
        self.addressTweet.getPlot(top10HashTags, folderPath,
                                  "top10HashTags.png", True)
        print("top10HashTags.png has been saved...")

        top10UserName = self.helper.loadPickle(os.path.join(folderPath,
                                                            "top10UserName.pkl"
                                                            ))
        self.addressTweet.getPlot(top10UserName, folderPath,
                                  "top10UserName.png", False)
        print("top10UserName.png has been saved...")

    # def getFinalHashTags(queries, originhashtags, getTwitter, start, end,
    #                      maxTweets, folderPath, filename, addressTweet, helper,
    #                      folderrootpath):
    #     """Get the final hashtags for finally getting results.
    #
    #     Test each hashtags in queries and filter out the general hashtags.
    #     """
    #     print ("Recording number of tweet with each hashtag...")
    #     tweetFlag = False
    #     for q in queries:
    #         for o in originhashtags:
    #             simScore = max(fuzz.token_set_ratio(o, q),
    #                            fuzz.partial_ratio(o, q) if
    #                            len(o) < len(q) else 0)
    #             if simScore > 70:
    #                 print ("******similar hashtags******")
    #                 print ("original hashtag {}".format(o))
    #                 break
    #         if simScore > 70:
    #             print ("new hashtag {}".format(q))
    #             continue
    #
    #         # get_address_twitter(helper, addressTweet, getTwitter, start, end,
    #         #                     query, folderPath, filename, maxTweets, tweetFlag)
    #         criterias = getTwitter.setCriteria(q, start, end, maxTweets)
    #         print (criterias)
    #         print ("crawling tweets with {}...".format(q))
    #         totalNumTweets = getTwitter.getTweets(criterias,
    #                                               os.path.join(folderPath,
    #                                                            'rawData'),
    #                                               filename, tweetFlag)
    #         print ("recording the number of tweets... {}:{}".format(q,
    #                                                                 totalNumTweets)
    #                )
    #         addressTweet.recordTweetNum(folderPath, q, totalNumTweets)
    #
    #     tweetNum = helper.loadJson(folderPath + '/tweetNum.json')
    #     tweetNum_sorted = addressTweet.sortDict(tweetNum)
    #     rm = []
    #     for st in tweetNum_sorted:
    #         for ot in originhashtags:
    #             if st[1] > tweetNum[ot]:
    #                 rm.append(st[0])
    #                 break
    #     finalH = [h for h in queries if h not in rm]
    #     return finalH

    def getHashtagPopularity(self, queries, originhashtags):
        """Get the hashtag popularity from google.

        Parameters
        ----------
        queries : list
            the list of hashtags
        originhashtags : list
            the list of original hashtags
        helper : object
            the helper object
        addressTweet : object
            the addressTweet object
        rootpath : str
            the root path of data
        folderpath : type
            the folderpath of data

        Returns
        -------
        None
            the result is stored into hashtagNum.json

        """
        for query in queries:
            query = query + " AND twitter"
            ghp = Utility.GetHashtagPopularity(query, self.rootpath,
                                               self.folderpath)
            ghp.start_crawl()
        htnPath = os.path.join(self.folderpath, 'experiment', 'google_test')
        hashtagsPopular = self.helper.loadJson(os.path.join(htnPath,
                                                            'hashtagNum.json'))
        print("the total hashtag popularity is {}".format(hashtagsPopular))
        # split the hashtagsPopular into original and new
        originHashtagsPopular = {}
        keys = hashtagsPopular.keys()
        for h in list(keys):
            if h in originhashtags:
                originHashtagsPopular[h] = hashtagsPopular[h]
                del hashtagsPopular[h]
        print("the original hashtag popularity is {}".format(originHashtagsPopular)
              )
        print("the filtered hashtag popularity is {}".format(hashtagsPopular))
        hashtagsPopular_sorted = self.addressTweet.sortDict(hashtagsPopular)
        rm = []
        for st in hashtagsPopular_sorted:
            for ot in originhashtags:
                # filter out hashtags: order of magnitudes(hashtags) > order of
                # magnitudes(original hashtags)
                if st[1] > originHashtagsPopular[ot]:
                    rm.append(st[0])
                    break
        filterH = [h for h, num in hashtagsPopular_sorted if h not in rm]
        print("filterH length is {}".format(len(filterH)))
        l = 20-len(list(originHashtagsPopular.keys()))
        print("need to add {} hashtags".format(l))
        finalH = filterH[:l] + list(originHashtagsPopular.keys())
        return finalH

    # @click.command()
    # @click.option('--rootpath', '-r', help='the root path of data')
    # @click.option('--originhashtag', '-o', help='the initial query')
    # @click.option('--start', '-s', help='the start date')
    # @click.option('--end', '-e', help='the end date')
    # @click.option('--folderrootpath', '-f', help='the path of the folder')
    # @click.option('--tweetflag', prompt='do you want to address tweet?',
    #               help='whether to address tweet')
    def start_getTweets(self):
        """Get tweets.

        Try 2 times to get tweets:
            1. get all the tweets with query
            2. get all the tweets with new query(top10 hashtags)
        """
        if 'AND' not in self.originhashtag:
            originhashtags = self.originhashtag.split()
            originquery = ' OR '.join(originhashtags)
        else:
            # originhashtags = originhashtag.split('AND')
            originhashtags = [self.originhashtag]
            originquery = self.originhashtag

        folderPath = os.path.join(self.folderpath, 'experiment')
        # filename = "tweets.pkl"
        maxTweets = 1000 * 1

        print("*" * 100)
        print("crawling with query {}...".format(originquery))

        self.get_address_twitter(originquery, folderPath, maxTweets)

        # update queries use the top10 hashtags
        top10HashTags = self.helper.loadPickle(os.path.join(folderPath,
                                                            'top10HashTags.pkl'
                                                            ))
        print(top10HashTags)
        top10ht = list(top10HashTags.keys())[:]
        print("original top10 hashtags {}".format(top10ht))

        # filtering
        queries = top10ht[:]
        if 'AND' in originquery:
            if originquery not in queries:
                queries.append(originquery)
        else:
            for ht in originhashtags:
                if ht not in queries:
                    queries.append(ht)

        filterH = self.getHashtagPopularity(queries, originhashtags)
        print("length of finalH is {}".format(len(filterH)))
        finalH = filterH[:]

        finalQ = ' OR '.join(finalH)
        print("*" * 100)
        print("finally crawling with query {}...".format(finalQ))
        # times += 1
        maxTweets = 3000
        folderPath = os.path.join(self.folderpath, 'final')
        self.get_address_twitter(finalQ, folderPath, maxTweets)
