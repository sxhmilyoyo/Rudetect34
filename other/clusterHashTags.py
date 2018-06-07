from AddressTweet import AddressTweet
import sys
sys.path.insert(0, './GetOldTweets-python')
import got
from Helper import Helper
import csv
from AHC import AHC
import json
from collections import defaultdict

if __name__ == '__main__':
	addressTweet = AddressTweet()
	print "getting hashtags..."
	hashTags2num = addressTweet.getHashTags("Texas Shooting/4/rawData/tweets.pkl")
	print "get hashtags."

	# test - get 20 hashtags from file
	helper = Helper()
	# sortedHashTags = helper.loadPickle("Texas Shooting/4/20Hashtags_test.pkl")
	# print sortedHashTags
	sortedHashTags = addressTweet.getSortedHashTags(hashTags2num)
	# test

	# test - save to csv
	'''
	labels = [i[0] for i in sortedHashTags]
	labels.insert(0, '')
	f = open("/local/data/haoxu/Rudetect/Texas Shooting/4/result.csv", "w")
	writer = csv.writer(f)
	writer.writerow(labels)
	for i in range(len(similarityMatrix)):
		similarityMatrix[i].insert(0, labels[i+1])
		writer.writerow(similarityMatrix[i])
	f.close()
	'''

	data = [i[0] for i in sortedHashTags if i[1] > 1]
	print "the length of data is %d" %len(data)

	ahc = AHC()

	print "getting distance matrix..."
	distance_matrix = ahc.get_distance_matrix(data)
	print "get distance matrix."
	helper.dumpPickle("Texas Shooting/4", "distance_matrix.pkl", distance_matrix)
	print "stored distance matrix."

	labels = [[i] for i in range(len(data))]

	print "start clustering..."
	clusters = ahc.agglomerate(labels, distance_matrix)
	print "finish clustering."

	print clusters

	result = [[] for i in range(len(clusters))]
	for i in range(len(clusters)):
		for n in clusters[i]:
			result[i].append(data[n])
	print result

	with open("/local/data/haoxu/Rudetect/Texas Shooting/4/clusters.json", "w") as fp:
		json.dump(result, fp, indent=4)