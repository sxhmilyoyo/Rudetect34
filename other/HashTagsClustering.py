import sys
sys.path.insert(0, './GetOldTweets-python')
import got
from fuzzywuzzy import fuzz
from Helper import Helper
from collections import defaultdict
import operator

class HashTagsClustering():

	def __init__(self):
		self.helper = Helper()

	def getHashTags(self, filePath):
		tweets = self.helper.loadPickle(filePath)
		hashTags2num = defaultdict(int)
		for tweet in tweets:
			hashTags2num[tweet.hashtags.lower()] += 1
		return hashTags2num

	def getSortedHashTags(self, hashtags):
		# test 20 hashtags
		sortedHashTags = sorted(hashtags.items(), key=operator.itemgetter(1), reverse=True)[:20]
		self.helper.dumpPickle("Texas Shooting/4", "20Hashtags_test.pkl", sortedHashTags)
		return sortedHashTags

	# def getSimilarity(self, sortedHashTags):
	# 	similarityMatrix = [[0 for j in range(len(sortedHashTags))] for i in range(len(sortedHashTags))]
	# 	for i in range(len(similarityMatrix)):
	# 		for j in range(len(similarityMatrix[i])):
	# 			similarityMatrix[i][j] = fuzz.token_set_ratio(sortedHashTags[i][0], sortedHashTags[j][0])
	# 	return similarityMatrix

		
