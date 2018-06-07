import os
import pickle
import sys
import time
import tweepy
from TweeterTest import TweeterTest
from collections import defaultdict
from datetime import datetime

def main():
	rootPath = '/local/data/haoxu/Rudetect'
	folderPath = '#DevinKelley'
	print "start testing Twitter Account from %s..." %folderPath

	tweetTest = TweeterTest()
	with open(os.path.join(rootPath, folderPath, 'userName.pkl')) as fp:
		userNameDict = pickle.load(fp)
	usernames = userNameDict.keys()

	tweeterScore = defaultdict(float)	
	for username in usernames:
		success = True
		otherError = False
		sleepTime = 60
		while success:
			try:
				result = tweetTest.testTwitter(username)
				success = False
			except tweepy.TweepError as e:
				print e
				try:
					print e.message[0]['code']
					if e.message[0]['code'] == 130:
						time.sleep(sleepTime)
						sleepTime *= 1.2
					else:
						success = False
						otherError = True
				except Exception as e:
					print e
					success = False
					otherError = True
			except Exception as e:
				print "not TweepError"
				print e
				success = False
				otherError = True
				
		# print username, result['user']['screen_name']
		if not otherError:
			if username != result['user']['screen_name']:
				print username, result['user']['screen_name']
				print "error: screenname != username"
				# sys.exit("screenname does not equal username")
			score = tweetTest.getScore(result)
			tweeterScore[username] = score
			# print "wait 5 secs..."
			time.sleep(5)
			# print "stop waiting."
			with open(os.path.join(rootPath, folderPath, 'tweeterScore.pkl'), 'w') as fp:
				pickle.dump(tweeterScore, fp)
	print "saved tweeterScore.pkl"


main()