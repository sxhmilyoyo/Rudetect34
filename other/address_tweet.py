import AddressTweet
import operator
import os
from collections import defaultdict
from Helper import Helper

if __name__ == '__main__':
	helper = Helper()

	addressTweet = AddressTweet.AddressTweet()
	# print "get hashtags..."
	# addressTweet.getHashtags('NYCattack')
	# print "get userIdName..."
	# addressTweet.getUserName('NYCattack')

	top10HashTags = helper.loadPickle(os.path.join('NYCattack', "top10HashTags.pkl"))
	addressTweet.getPlot(top10HashTags, 'NYCattack', "top10HashTags.png", True)
	print "top10HashTags.png has been saved..."

	top10UserName = helper.loadPickle(os.path.join('NYCattack', "top10UserName.pkl"))
	addressTweet.getPlot(top10UserName, 'NYCattack', "top10UserName.png", False)
	print "top10UserName.png has been saved..."