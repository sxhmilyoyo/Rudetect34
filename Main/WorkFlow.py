import codecs
import os
import random
import time
from collections import defaultdict
import numpy as np
import Clustering
import Evaluate
import got3
import Information
import OpinionMining
import SVO
import Twitter
import Utility
from chowmein import label_topic
from gensim.models.word2vec import LineSentence, Word2Vec


class WorkFlow(object):
    """The workfolw of the system."""

    def __init__(self, rootpath, folderpath):
        """Initialize the parameters.

        Parameters
        ----------
        rootpath : str
            the root path of the data
        folderpath : str
            the fodler path of the data

        Returns
        -------
        None

        """
        self.rootpath = rootpath
        self.folderpath = folderpath
        self.helper = Utility.Helper(rootpath)
        self.preprocessData = Utility.PreprocessData(rootpath)

    def getTweets(self, query, start, end):
        """Get the the final tweets.

        Returns
        -------
        None

        """
        gettweets = Twitter.GetTweets(self.rootpath, self.folderpath,
                                      start, end, query)
        gettweets.start_getTweets()

    def getWord2Vec(self):
        """Get the word2vec model from all the corpus.

        Returns
        -------
        None

        """
        folderPath = os.path.join(self.rootpath, self.folderpath, 'final')
        tweets = self.helper.getTweet(os.path.join(self.folderpath, 'final'))
        with codecs.open(os.path.join(folderPath,
                                      "tweets_line_word2vec.txt"),
                         "w", encoding='utf8') as fp:
            for tweet in tweets:
                # print (type(tweet.text.encode('utf8')))
                c1 = self.preprocessData.cleanTweet(tweet.text)
                c2 = self.preprocessData.cleanTweet4Word2Vec(c1)
                fp.write(c2.lower() + '\n')

        data4word2vec = LineSentence(os.path.join(folderPath,
                                                  "tweets_line_word2vec.txt"))
        if not os.path.exists(os.path.join(self.rootpath, 'w2vmodel')):
            print("Start training word2vec model with {}...".format(self.folderpath)
                  )
            model = Word2Vec(sentences=data4word2vec, size=100,
                             alpha=0.025, window=5, min_count=5,
                             sample=0, seed=1, workers=1, min_alpha=0.0001,
                             sg=1, hs=1, negative=5, cbow_mean=0
                             )
        else:
            print("Start updating word2vec model with {}...".format(self.folderpath)
                  )
            model = Word2Vec.load(os.path.join(self.rootpath, 'w2vmodel'))
            model.build_vocab(data4word2vec, update=True)
            model.train(data4word2vec, total_examples=model.corpus_count,
                        epochs=model.iter)
        model.save(os.path.join(self.rootpath, "w2vmodel"))
        print("Finished training word2vec and saved it as w2vmodel.")

    def getTopicPmi(self, folderpath, numTopic):
        """Get topic with pmi.

        Parameters
        ----------
        folderpath : str
            the assigned folder path
        numTopic : int
            the number of the topic for the LDA

        Returns
        -------
        numpy.array
            the array of topic word distributions

        """
        # get tweets
        # helper = Utility.Helper(self.rootpath)
        folderPath = os.path.join(folderpath, 'final')
        tweets = self.helper.getTweet(folderPath)
        with codecs.open(os.path.join(self.rootpath, folderPath,
                                      "tweets_line.txt"),
                         "w", encoding='utf8') as fp:
            for tweet in tweets:
                # print (type(tweet.text.encode('utf8')))
                c1 = self.preprocessData.cleanTweet(tweet.text)
                fp.write(c1 + '\n')

        # get topic with pmi
        corpus_path = os.path.join(self.rootpath, folderPath, "tweets_line.txt"
                                   )
        n_topics = numTopic
        n_top_words = 5
        preprocessing_steps = ['tag']
        n_cand_labels = 100
        label_min_df = 5
        label_tags = ['NN,NN', 'JJ,NN']
        n_labels = 3
        lda_random_state = 12345
        lda_n_iter = 10000

        labels, words, dist = label_topic.get_topic_labels(corpus_path,
                                                           n_topics,
                                                           n_top_words,
                                                           preprocessing_steps,
                                                           n_cand_labels,
                                                           label_min_df,
                                                           label_tags,
                                                           n_labels,
                                                           lda_random_state,
                                                           lda_n_iter)
        print("\nTopical labels:")
        print("-" * 20)
        topics = defaultdict(list)
        for i, labels in enumerate(labels):
            topics[i] = map(lambda l: ' '.join(l), labels)
            print(u"Topic {}: {}".format(i, ', '.join(map(lambda l:
                                                          ' '.join(l),
                                                          labels))
                                         )
                  )
        self.helper.dumpJson(folderPath, "tweets_label_words_pmi.json",
                             labels)
        print("tweets_topic_label_pmi.json has been saved.")
        self.helper.dumpJson(folderPath, "tweets_topic_words_pmi.json",
                             words)
        print("tweets_topic_words_pmi.json has been saved.")
        return dist

    def getCluster(self, vectorizer, numclusters):
        """Get main function for getCluster.

        Parameters
        ----------
        vectorizer : str
            the vectorizer used in addressing word2vec
            options: 'mean', 'tfidf'
        numclusters : int
            the number of clusters

        Returns
        -------
        None

        """
        folderPath = os.path.join(self.folderpath, 'final')
        vectorizer = vectorizer
        numClusters = numclusters
        preprocessor = Utility.PreprocessData(self.rootpath)
        gc = Clustering.GetCluster(vectorizer, self.rootpath)
        # get the kmeans model
        print("Getting the k-means model...")
        startTime = time.time()
        km = gc.getKmeans(folderPath, numClusters)
        print("---------- K-means: {} seconds ----------".
              format(time.time() - startTime))
        # get the doc2Label
        print("Getting doc to label...")
        gc.getDoc2Label(folderPath, km)
        # get Label2Doc
        print("Getting label to doc...")
        gc.getLabel2Doc(folderPath, km)
        # get tweets.pkl for each clusters
        print("Storing tweets for clusters...")
        preprocessor.storeTweets4Clusters(folderPath)

    def getSubject(self, query):
        """Get subject.

        Arguments:
            query {str} -- the initial query
        """
        # folderPath = os.path.join(folderpath, 'final')
        # fullPath = os.path.join(self.rootpath, folderPath)
        svoExtractor = SVO.SvoExtractor(self.rootpath, self.folderpath)
        tweets = self.helper.getTweet(self.folderpath)
        tweets_list = []
        cleanedTweets = []
        for tweet in tweets:
            tweets_list.append(tweet)
            c1 = self.preprocessData.cleanTweet(tweet.text)
            cleanedTweets.append(c1)
        print("Parsing...")
        sortedSubject2Number, subject2tweetInfo, parsedTweets = svoExtractor.collectSubject(
            tweets_list, cleanedTweets)
        # sortedSubject2Number = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "sorted_subject2number.json"))
        # subject2tweetInfo = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "subject2tweetInfo.json"))
        # parsedTweets = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "tweets_id2Info.json"))
        candidateClaims = svoExtractor.extractSvo(
            sortedSubject2Number, subject2tweetInfo, parsedTweets, 6)

        svoExtractor.rankClaims(query[1:], tweets_list, candidateClaims)

        # for subject in subjects:
        #     print("extracting for subject: {}".format(subject))
        #     print(self.rootpath)
        #     taggedSents = svoExtraction.tag_sentences(self.rootpath, subject,
        #                                               document)
        #     # print(taggedSents)
        #     svos = [
        #         (svoExtraction.get_svo(sentence, subject), idx)
        #         for sentence, idx in taggedSents
        #     ]
        #     # address svos
        #     filteredSvos = self.preprocessData.getTop5SVO(folderPath, svos)
        #     # print(filteredSvos)
        #     subject2svos[subject] = filteredSvos

        # self.helper.dumpJson(folderPath, 'subject2svos.json', subject2svos)
        # print("subject2svos.json has been saved.")

    def getQuery(self, folderpath):
        """Get query for svo of each cluster.

        Save the subject2queries.json for each cluster
        Returns
        -------
        None

        """
        queryGenerator = Information.QueryGenerator(self.rootpath)
        print("Getting query for {}".format(folderpath))
        queryGenerator.generateQuery(folderpath)

    def getSnippets(self, folderpath):
        """Get the google search snippets.

        Parameters
        ----------
        fullPath : str
            full path of folder

        Returns
        -------
        None

        """
        print("Getting snippets for {}".format(folderpath))
        # s2q = self.helper.loadJson(os.path.join(folderpath, 'final',
        #                                         'subject2svoqueries.json'))
        queries = self.helper.loadCsv(
            folderpath+"/final", "candidate_queries.csv")
        fullPath = os.path.join(self.rootpath, folderpath)

        relevant = []
        for idx, query in enumerate(queries):
            print("Crawling query {} ...".format(query[1]))
            googleSnippets = Information.GoogleSnippets(fullPath, query[0],
                                                        idx, query[1])
            res = googleSnippets.start_crawl()
            relevant.append(res)
            time.sleep(random.randint(1, 11))
        # for topic in s2q:
        #     relevant = []
        #     for idx, t in enumerate(s2q[topic]):
        #         # print("Searching for topic {} with query {}".format(topic,
        #         #                                                     query))
        #         googleSnippets = Information.GoogleSnippets(fullPath, topic,
        #                                                     idx, t['query'])
        #         res = googleSnippets.start_crawl()
        #         relevant.append(res)
        #         time.sleep(random.randint(1, 11))
        output_root = os.path.join(folderpath, 'final')
        self.helper.dumpJson(output_root, "snippets.json", relevant)
        # output_root = os.path.join(folderpath, 'final', 'snippets')
        # if not os.path.exists(output_root):
        # os.makedirs(output_root)
        # self.helper.dumpJson(output_root, "snippets.json", total_snippets)

    def getOpinion(self, folderpath):
        """Get the opinion for each cluster.

        Parameters
        ----------
        folderpath : str
            the folder path of the data

        Returns
        -------
        list
            [
                {"text": ..., "id": ..., "polarity": ...},
                {"text": ..., "id": ..., "polarity": ...}
            ]

        """
        sentiment140 = OpinionMining.Sentiment140API()

        folderPath = os.path.join(self.rootpath, folderpath, 'final',
                                  'snippets')
        svoQuery = self.helper.loadJson(os.path.join(self.rootpath, folderpath,
                                                     'final', 'subject2svoqueries.json'))
        subjectFolderPaths = os.listdir(folderPath)
        for subjectFolderPath in subjectFolderPaths:
            svos = [sq['svo'] for sq in svoQuery[subjectFolderPath]]
            filenames = os.listdir(os.path.join(folderPath, subjectFolderPath))
            data4svos = []
            for filename in filenames:
                # get opinion for svo
                idx = int(filename[0])
                data4svos.append({'text': svos[idx],
                                  'id': idx})
                # get opinions for snippets
                fullPath = os.path.join(folderPath, subjectFolderPath, filename
                                        )
                snippets = self.helper.loadJson(fullPath)
                data4snippets = []
                for snippet in snippets:
                    data4snippets.append({'text': snippet['snippets'],
                                          'id': int(snippet['id'][-1])})
                result4snippets = sentiment140.bulk_classify_json(
                    data4snippets)
                self.helper.dumpJson(os.path.join(folderPath,
                                                  subjectFolderPath),
                                     filename[:-5] + '_opinion.json',
                                     result4snippets)
            result4svo = sentiment140.bulk_classify_json(data4svos)
            self.helper.dumpJson(os.path.join(folderPath,
                                              subjectFolderPath),
                                 'svos_opinion.json', result4svo)
            print("opinions for {} have been saved.".format(subjectFolderPath))

    def getCorpus4Classification(self, folderpath, flag):
        """Get corpus as .csv file for further classification.        
        Arguments:
            folderpath {str} -- the path to data folder
            flag {str} -- 'event': get corpus for whole tweets.
                          'cluster': get corpus for each cluster.
        """

        folderPath = os.path.join(folderpath, 'final')
        if flag == 'cluster':
            s2vs = self.helper.loadJson(folderPath+"/subject2svoqueries.json")
            subjects = []
            for subject in s2vs:
                if s2vs[subject]:
                    subjects.append(subject)
            self.helper.dumpJson(folderPath, 'target.json', subjects)
            targets = ';'.join(subjects)
            if os.path.exists(os.path.join(self.rootpath, self.folderpath, 'totalTargets.json')):
                totalTargets = self.helper.loadJson(
                    self.folderpath+'/totalTargets.json')
                totalTargets.append(targets)
                self.helper.dumpJson(
                    self.folderpath, 'totalTargets.json', totalTargets)
            else:
                self.helper.dumpJson(
                    self.folderpath, 'totalTargets.json', [targets])
        elif flag == 'event':
            totalTargets = self.helper.loadJson(
                folderpath+'/totalTargets.json')
            targets = ';'.join(totalTargets)
        self.preprocessData.getCorpus4csv(folderPath, targets)
        self.preprocessData.getCorpus4csvFromStatements(folderPath)
        self.preprocessData.getCorpus4csvFromSnippets(folderPath)

    def getSimilarity4Statements(self, folderpath):
        """Get similarity between candiadate statements and target statement."""
        getSimilarity = Evaluate.GetSimilarity('tfidf', self.rootpath)
        tokens_statements, id2candiadateStatements = getSimilarity.getCorpusFromCandidateStatements(
            folderpath)
        tokens_target = getSimilarity.getCorpusFromTargetStatements(folderpath)
        # print("tokens_statements", len(tokens_statements))
        # print("tokens_target", tokens_target)
        vectors_candidates = getSimilarity.getVector(tokens_statements)
        vector_target = getSimilarity.getVector(tokens_target)
        # print("vectors_candidates", vectors_candidates[0:1].shape)
        # print("vector_target", vector_target.shape)
        similarities = getSimilarity.getCosineSimilarity(
            vectors_candidates, vector_target)
        # print(similarities, vectors_candidates)
        # print(similarities[0], len(similarities[0]))

        # average, max, min
        maximum = max(similarities[0])
        print("max: {}".format(maximum))

        id2similarities = dict(enumerate(list(similarities[0])))
        data = []
        for key in id2candiadateStatements:
            data.append([id2candiadateStatements[key], id2similarities[key]])
        self.helper.dumpCsv(
            folderpath+"/final", "similarities.csv", ['statement', 'similarity'], data)

    def getSimilarityStatements2Tweets(self, folderpath):
        """Get similarity between candidate statements and tweets.

        Arguments:
            folderpath {str} -- the path to data folder

        Returns:
            None -- index_candiadate_statement_2_index_tweet.json and index_tweet_2_index_candiadate_statement.json are generated.
        """
        getSimilarity = Evaluate.GetSimilarity('tfidf', self.rootpath)
        tokens_statements, id2candiadateStatements = getSimilarity.getCorpusFromCandidateStatements4Cluster(
            folderpath)
        print("length of statements ", len(tokens_statements))

        tokens_tweets, id2tweets = getSimilarity.getCorpusFromTweets4Cluster(
            folderpath)
        print("length of tweets ", len(tokens_tweets))

        # return None if any of them is None
        if len(tokens_statements) == 0 or len(tokens_tweets) == 0:
            print("no statements or tweets.")
            return
        vectors_candidates = getSimilarity.getVector(tokens_statements)
        print("shape of vectors_candidates ", vectors_candidates.shape)
        vector_tweets = getSimilarity.getVector(tokens_tweets)
        print("shape of vector_tweets ", vector_tweets.shape)

        # shape is #vector_tweets x #vectors_candidates
        similarities = getSimilarity.getCosineSimilarity(
            vectors_candidates, vector_tweets)
        print("shape of similarities ", similarities.shape)

        # get max indeices of candidates statement for each tweet
        index_tweet_2_max_index_candiadate_statement = enumerate(
            list(np.argmax(similarities, axis=1)))
        self.helper.dumpJson(folderpath+"/final", "index_tweet_2_index_candiadate_statement.json",
                             index_tweet_2_max_index_candiadate_statement)
        # reverse the key and value
        max_index_candiadate_statement_2_index_tweet = defaultdict(list)
        for tid, sid in index_tweet_2_max_index_candiadate_statement:
            max_index_candiadate_statement_2_index_tweet[sid].append(tid)
        self.helper.dumpJson(folderpath+"/final", "index_candiadate_statement_2_index_tweet.json",
                             max_index_candiadate_statement_2_index_tweet)

    def run4cluster(self):
        """Run getTopicPmi, extractSVOs and getQuery for each cluster.

        Returns
        -------
        None

        """
        folderPath = os.path.join(self.folderpath, 'final/clusterData')
        foldernames = [i for i in os.listdir(os.path.join(
            self.rootpath, folderPath)) if os.path.isdir(os.path.join(self.rootpath, folderPath, i))]
        for foldername in foldernames:
            # if foldername != '1':
            #     continue
            print(foldername)
            folderFullPath = os.path.join(folderPath, foldername)
            print(folderFullPath)
            print("Running code for {}".format(folderFullPath))
            print("Running getTopicPmi.py ...")
            # subprocess.call(args)
            try:
                self.getTopicPmi(folderFullPath, 1)
            except Exception as e:
                print("ERROR!!!")
                print(e)

            print("Running extractSVOs ...")
            self.extractSVOs(folderFullPath)
            print("Running getQuery ...")
            self.getQuery(folderFullPath)
            print("Running getSimilarityStatements2Tweets ...")
            self.getSimilarityStatements2Tweets(folderFullPath)
            print("Runnig getSnippets ...")
            self.getSnippets(folderFullPath)
            print("Running getCorpus4Classification ...")
            self.getCorpus4Classification(folderFullPath, 'cluster')
