from HDP import HDP
from PreprocessData import PreprocessData

if __name__ == '__main__':
	hdp = HDP()
	preprocessData = PreprocessData()
	folderName = ""

	# preprocessing the data
	corpus = preprocessData.getCorpus_old(os.path.join(folderName, "rawData"))
	corpusDict = {}
	for k, corpua in enumerate(corpus):
		corpusDict[k] = corpua

	# training hdp model
	hdp.buildDict(folderName, corpus)
	hdp.convertDocBow(olderName, dictionary, corpus)
	hdp.convertBowTfidf(folderName, dataBow, dictionary)
	hdpModel = hdp.getTopicModel(folderName)

	# getting {doc: [topics]}
	doc2topics = {}
	for k in corpusDict:
		doc2topics[k] = hdpModel[corpusDict[k]]
