from gensim import corpora
from gensim.models import TfidfModel
import os
import json

class HDP():
	def __init__(self):
		self.rootPath = "/local/data/haoxu/Rudetect"

	def buildDict(self, folderName, corpus):
		print "start building dict..."
		dictionary = corpora.Dictionary(corpus)
		dictionary.save(os.path.join(self.rootPath, folderName, "data.dict"))
		print "data.dict has been saved."
		# print dictionary.token2id
		# return dictionary

	def convertDocBow(self, folderName, dictionary, corpus):
		print "start building bow mm..."
		corpusBow = [dictionary.doc2bow(corpora) for corpora in corpus]
		corpora.MmCorpus.serialize(os.path.join(self.rootPath, "dataBow.mm"), corpusBow)
		print "dataBow.mm has been saved."
		# return corpus_bow

	def convertBowTfidf(self, folderName, dataBow, dictionary):
		print "start building tfidf..."
		tfidf = TfidfModel(dataBow, id2word=dictionary, normalize=True)
		tfidf.save("data.tfidfModel")
		corpora.MmCorpus.serialize("dataTfidf.mm", tfidf[dataBow], progress=10000)
		print "data.tfidfModel and dataTfidf.mm have been saved."

	def getTopicModel(folderName):
		corpus = corpora.MmCorpus(os.path.join(self.rootPath, folderName, "dataBow.mm"))
		dictionary = corpora.Dictionary.load(os.path.join(self.rootPath, folderName, "data.dict"))
		hdpModel = models.hdpmodel.HdpModel(corpus=corpus, id2word=dictionary)
		hdpModel.save(os.path.join(self.rootPath, folderName, "data.hdpModel"))
		print "hdp model has been saved."
		return hdpModel
		
