import CMUTweetTagger
from Utility.Helper import Helper
import os
from collections import defaultdict


class SvoExtractor(object):
    """Extract the SVOs.

    Using the CMU TweetNLP ark-tweet-nlp-python wrapper.
    """

    def __init__(self, rootpath="", folderpath=""):
        self.helper = Helper(rootpath)
        self.rootpath = rootpath
        self.folderpath = folderpath
        self.fileFolderPath = os.path.join(
            self.rootpath, self.folderpath, "final")

    def tag(self, tweets):
        """Tag the tweets.

        Arguments:
            tweets {list} -- a list of tweet

        Returns:
            list -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]
        """
        taggedTweets = CMUTweetTagger.runtagger_parse(tweets)
        mergedNounTaggedTweets = self.mergeNoun(taggedTweets)
        self.helper.dumpJson(
            self.fileFolderPath, "tagged_tweets.json", taggedTweets)
        self.helper.dumpJson(
            self.fileFolderPath, "merged_noun_tagged_tweets.json", mergedNounTaggedTweets)
        print("merged_noun_tagged_tweets.json has been saved.")
        return mergedNounTaggedTweets

    def mergeNoun(self, taggedTweets):
        """Merge the adjacent word with Noun Pos Tag.

        Noun with the POS tags: N, ^, S
        Arguments:
            taggedTweets {list} -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]

        Returns:
            newMergedTaggedTweets -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]
        """
        index = 0
        newMergedTaggedTweets = []
        for taggedTweet in taggedTweets:
            newMergedTaggedTweet = []
            print("length of tweet ", len(taggedTweet))
            # for i in range(index, len(taggedTweet)):
            while index < len(taggedTweet):
                print(index)
                merge = list(taggedTweet[index])
                if merge[1] in set(["N", "^", "S"]):
                    j = index + 1
                    while j < len(taggedTweet):
                        if taggedTweet[j][1] in set(["N", "^", "S"]):
                            merge[0] = merge[0] + " " + taggedTweet[j][0]
                            merge[1] = "N"
                            merge[2] = (merge[2] + taggedTweet[j][-1]) / 2
                            j += 1
                        else:
                            index = j
                            print("index is ", index)
                            break
                    index = j
                else:
                    index += 1
                newMergedTaggedTweet.append(tuple(merge))
        newMergedTaggedTweets.append(newMergedTaggedTweet)
        return newMergedTaggedTweets

    def extractNoun(self, mergedNounTaggedTweets):
        """Extract the Noun in merged Noun tagged tweets.

        Noun with the POS tags: N, ^, S
        Arguments:
            taggedTweets {list} -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]
        """
        noun2number = defaultdict(int)
        nounPOSTags = set(["N", "^", "S"])
        for taggedTweet in mergedNounTaggedTweets:
            for word, posTag, score in taggedTweet:
                if posTag in nounPOSTags:
                    noun2number[word] += 1
        self.helper.dumpJson(self.fileFolderPath,
                             "noun2number.json", noun2number)
        print("noun2number.json has been saved.")
