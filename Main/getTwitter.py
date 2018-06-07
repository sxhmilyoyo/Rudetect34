import time
from datetime import datetime
import sys
sys.path.insert(0, '..')
from Twitter.GetTwitterData import GetTwitterData

def main():
	# Las Vegas shooting
	# query = "Manhattan OR attack #NYCStrong OR #NYC OR #Manhattan OR #tribeca OR #TriBeCa OR #LowerManhattan OR World OR Trade OR Center"
	# starts = ["2017-10-31"]
	# ends = ["2017-11-01"]
	# filenames = ["NYCattack.pkl"]
	# maxTweets = 10000

	# victim of TexasChurchMassacre is Antifa
	query = "TexasChurchMassacre Antifa"
	start = "2017-11-05"
	end = "2017-11-07"
	folderPath = 'TexasChurchMassacre OR Antifa/rawData'
	filename = "TexasChurchMassacre_Antifa.pkl"
	maxTweets = 10000

	# devinpatrickkelley Antifa
	query = "devinpatrickkelley Antifa"
	start = "2017-11-05"
	end = "2017-11-07"
	folderPath = 'devinpatrickkelley Antifa/rawData'
	filename = "devinpatrickkelley_Antifa.pkl"
	maxTweets = 10000

	getTwitter = GetTwitterData()

	# tuples = zip(starts, ends, filenames)
	# for start, end, filename in tuples:
	print "start crawling from %s to %s with file %s" %(start, end, filename)
	criteria = getTwitter.setCriteria(query, start, end, maxTweets)
	print "crawling tweets..."
	getTwitter.getTweets(criteria, folderPath, filename)


main()
