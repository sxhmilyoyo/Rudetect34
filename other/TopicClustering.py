from fuzzywuzzy import fuzzy
from Helper import Helper
from collections import defaultdict
import operator

class TopicClustering():

	def __init__(self):
		self.helper = Helper()

	def getHashTags(filePath):
		tweets = self.helper.loadPickle(filePath)
		hashTags2num = defaultdict(int)
		for tweet in tweets:
			hashTags2num[tweet.hashtags.lower()] += 1
		return hashTags2num

	def getSortedHashTags(hashtags):
		return sorted(hashtags.items(), key=operator.itemgetter(1))[:20]

	def getSimilarity(sortedHashTags):
		similarityMatrix = [[0 for j in range(len(sortedHashTags))] for i in range(len(sortedHashTags))]
		for i in range(len(similarityMatrix)):
			for j in range(len(similarityMatrix[i])):
				similarityMatrix[i][j] = fuzzy.token_set_ratio(sortedHashTags[i][0], sortedHashTags[j][0])
		return similarityMatrix

		
