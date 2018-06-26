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
import Claim
import Twitter
import Utility
from chowmein import label_topic
from gensim.models.word2vec import LineSentence, Word2Vec
from pathlib import Path


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
        root = Path(self.rootpath)
        events = [x for x in root.iterdir() if x.is_dir()]

        tweets_line_word2vec_path = root / "tweets_line_word2vec.txt"
        if tweets_line_word2vec_path.exists():
            os.remove(str(tweets_line_word2vec_path))
        with codecs.open(str(tweets_line_word2vec_path), "a") as fp:
            for event in events:
                print("addressing with {}".format(str(event)))
                total = 0
                tweets = self.helper.getTweet(str(event.name))
                for tweet in tweets:
                    # print (type(tweet.text.encode('utf8')))
                    c1 = self.preprocessData.cleanTweet(tweet.text)
                    fp.write(c1 + '\n')
                    total += 1
                print("total tweets is {}".format(total))

        data4word2vec = LineSentence(str(root / "tweets_line_word2vec.txt"))
        w2vmodelPath = root / "w2vmodel"
        if not w2vmodelPath.exists():
            print("Start training word2vec model with {}...".format(str(root))
                  )
            model = Word2Vec(sentences=data4word2vec, size=200,
                             alpha=0.025, window=5, min_count=5,
                             sample=0, seed=1, workers=1, min_alpha=0.0001,
                             sg=1, hs=1, negative=5, cbow_mean=0
                             )
        else:
            print("Start updating word2vec model with {}...".format(str(root))
                  )
            model = Word2Vec.load(str(root / 'w2vmodel'))
            model.build_vocab(data4word2vec, update=True)
            model.train(data4word2vec, total_examples=model.corpus_count,
                        epochs=model.iter)
        model.save(str(root / "w2vmodel"))
        w2v = model.wv
        w2v.save_word2vec_format(str(root / "w2v.bin"), binary=True)
        print("Finished training word2vec model and saved it as w2vmodel.")
        print("Finished training word2vec vectors and saved it as w2v.bin.")

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

    def getClaims(self, query):
        """Get claims.

        Arguments:
            query {str} -- the initial query
        """
        # folderPath = os.path.join(folderpath, 'final')
        # fullPath = os.path.join(self.rootpath, folderPath)
        self.preprocessData.generateTweetsLines(self.folderpath)

        claimExtractor = Claim.ClaimExtractor(self.rootpath, self.folderpath)
        getSimilarity = Claim.GetSimilarity(
            "/home/hao/Workplace/HaoXu/Data/skip_thoughts/pretrained/skip_thoughts_uni_2017_02_02/exp_vocab",
            "model.ckpt-501424")

        tweets = self.helper.getTweet(self.folderpath)
        tweets_list = []
        cleanedTweets = []
        for tweet in tweets:
            tweets_list.append(tweet)
            c1 = self.preprocessData.cleanTweet(tweet.text)
            cleanedTweets.append(c1)
        print("Parsing...")
        mergedNoun, sortedSubject2Number, subject2tweetInfo, parsedTweets = claimExtractor.collectSubject(
            tweets_list, cleanedTweets)
        # sortedSubject2Number = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "sorted_subject2number.json"))
        # subject2tweetInfo = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "subject2tweetInfo.json"))
        # parsedTweets = self.helper.loadJson(
        #     os.path.join(self.folderpath, "final", "tweets_id2Info.json"))
        candidateClaimsMergedClause = claimExtractor.getCandidateClaims(
            tweets_list, mergedNoun, sortedSubject2Number, subject2tweetInfo,
            parsedTweets, query[1:])
        # mergedCandidateClaims = claimExtractor.mergeSimilarSubjects(
        #     candidateClaims)
        similarClaimsComponents = getSimilarity.getSimilarClaims(
            candidateClaimsMergedClause, tweets)
        self.helper.dumpJson(self.folderpath+"/final",
                             "similar_claims_components.json", similarClaimsComponents)
        print("similar_claims_components.json has been saved.")
        # claimExtractor.rankClaims(
        #     query[1:], tweets_list, candidateClaimsMergedClause)

    def getSimilarTweets4Claim(self):
        # get claims
        claims = list(self.helper.getClaim(self.folderpath))
        # lowercase
        # claims = [claim.lower() for claim in claims]
        # get tweets
        tweets = self.helper.getTweet(self.folderpath)
        cleanedTweets = []
        for tweet in tweets:
            # tweets_list.append(tweet)
            c1 = self.preprocessData.cleanTweet(tweet.text)
            cleanedTweets.append(c1)
        getSimilarity = Claim.GetSimilarity(
            "/home/hao/Workplace/HaoXu/Data/skip_thoughts/pretrained/skip_thoughts_uni_2017_02_02/exp_vocab",
            "model.ckpt-501424")

        sentences, tweetIndex = getSimilarity.splitSentences(
            cleanedTweets)
        encodedSentences = getSimilarity.encodeSen(sentences)

        # for index, claim in enumerate(claims):
        encodedClaims = getSimilarity.encodeSen(claims)
        claims2tweets = getSimilarity.getTweets4Claims(
            sentences, encodedSentences, claims, encodedClaims, tweetIndex)

        for claimID, sentInfos in claims2tweets.items():
            claims2tweets[claimID] = self.preprocessData.sortListofLists(
                sentInfos, False)
        self.helper.dumpJson(
            self.folderpath, "final/sorted_claims2tweets.json", claims2tweets)
        print("sorted_claims2tweets.json have been saved.")

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
        tokens_candidates, id2claims = getSimilarity.getCorpusOfCandidateClaims(
            folderpath)
        tokens_target = getSimilarity.getCorpusOfTargetClaim(folderpath)
        # print("tokens_statements", len(tokens_statements))
        # print("tokens_target", tokens_target)
        vectors_candidates = getSimilarity.getVector(tokens_candidates)
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
        for key in id2claims.keys():
            data.append([id2claims[key], id2similarities[key]])
        self.helper.dumpCsv(
            folderpath+"/final", "similarities.csv", ['statement', 'similarity'], data)

    def getSimilarityStatements2Tweets(self, folderpath):
        """Get similarity between candidate claims and tweets.

        Arguments:
            folderpath {str} -- the path to data folder

        Returns:
            None -- index_tweet_2_index_candidate_claim.json;
                    index_candidate_claim_2_index_tweet.json;
                    index_candidate_claim_2_tweet.json are generated.
        """
        getSimilarity = Evaluate.GetSimilarity('tfidf', self.rootpath)
        tokens_claims, id2claims = getSimilarity.getCorpusOfCandidateClaims(
            folderpath)
        print("length of statements ", len(tokens_claims))

        tokens_tweets, id2tweets = getSimilarity.getCorpusOfTweets(
            folderpath)
        print("length of tweets ", len(tokens_tweets))

        # return None if any of them is None
        if len(tokens_claims) == 0 or len(tokens_tweets) == 0:
            print("no statements or tweets.")
            return
        vectors_claims = getSimilarity.getVector(tokens_claims)
        print("shape of vectors_claims ", vectors_claims.shape)
        vector_tweets = getSimilarity.getVector(tokens_tweets)
        print("shape of vector_tweets ", vector_tweets.shape)

        # shape is #vector_tweets x #vectors_candidates
        similarities = getSimilarity.getCosineSimilarity(
            vectors_claims, vector_tweets)
        print("shape of similarities ", similarities.shape)

        # get max indices of candidates statement for each tweet
        index_tweet_2_max_index_candidate_claim = enumerate(
            list(np.argmax(similarities, axis=1)))
        self.helper.dumpJson(folderpath+"/final",
                             "index_tweet_2_index_candidate_claim.json",
                             index_tweet_2_max_index_candidate_claim)
        # reverse the key and value
        max_index_candidate_claim_2_index_tweet = defaultdict(list)
        for tid, sid in index_tweet_2_max_index_candidate_claim:
            max_index_candidate_claim_2_index_tweet[sid].append(tid)
        self.helper.dumpJson(folderpath+"/final",
                             "index_candidate_claim_2_index_tweet.json",
                             max_index_candidate_claim_2_index_tweet)
        # generate {index_claim: [tweet1, tweet2, ...]}
        index_candidate_claim_2_tweet = defaultdict(list)
        for index_candidate_claim in max_index_candidate_claim_2_index_tweet.keys():
            for index_tweet in max_index_candidate_claim_2_index_tweet[index_candidate_claim]:
                index_candidate_claim_2_tweet[index_candidate_claim].append(
                    id2tweets[index_tweet])
        self.helper.dumpJson(os.path.join(
            folderpath, "final"), "index_candidate_claim_2_tweet.json",
            index_candidate_claim_2_tweet)
        print("index_candidate_claim_2_tweet.json has been saved.")

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
