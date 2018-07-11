import os
import numpy as np
import scipy.spatial.distance as sd
from nltk import sent_tokenize
from nltk import word_tokenize
from collections import defaultdict
import Utility
from sklearn.cluster import DBSCAN
from .SkipThoughtsModel import SkipThoughtsModel
from .Sent2Vec import Sent2Vec


class GetSimilarity(object):
    """Get similar tweets for claim or claims based on sen2vec in skip thoughts model."""

    def __init__(self, rootPath, folderPath, model=None):
        """Initialize the TweetsExtractor4Claim model.

        Arguments:
            rootPath {str} -- the path to data root folder
            folderPath {str} -- the event name
            model {dict} -- model information
        """
        self.helper = Utility.Helper(rootPath)
        self.fileFolderPath = os.path.join(folderPath, "final")
        if model:
            if model["name"] == "skipthoughts":
                self.model = SkipThoughtsModel(
                    model["modelPath"], model["checkpointPath"])
            if model["name"] == "sent2vec":
                self.model = Sent2Vec(model["modelPath"])

    def splitSentences(self, cleanedTweets):
        """Split sentences in each tweet.

        Arguments:
            cleanedTweets {list} -- a list of cleaned tweets

        Returns:
            tuple -- (sentences, tweetIndices)
        """
        sentences = []
        tweetIndex = []
        for index, tweet in enumerate(cleanedTweets):
            sents = sent_tokenize(tweet)
            for sent in sents:
                if len(word_tokenize(sent)) >= 3:
                    sent = Utility.PreprocessData.removePunctuation(sent)
                    # sentences.append(sent.lower())
                    sentences.append(sent)
                    tweetIndex.append(index)
        return sentences, tweetIndex

    # def encodeSen(self, sentences):
    #     """Encode the sentences based on the sent2vec model.

    #     Arguments:
    #         sentences {list} -- a list of sentences

    #     Returns:
    #         list -- a list of encoded sentences
    #     """

    #     encodedSentences = self.encoder.encode(sentences)

    #     return encodedSentences

    def getTweets4Claims(self, sentences, encodedSentences, claims, encodedClaims, tweetIndex, num=10):
        """Get tweets for claim.

        Arguments:
            sentences {list} -- a list of sentences
            encodedSentences {np.array} -- a list of encoded sentences
            claims {list} -- a list of claims
            encodedClaims {np.array} -- a list of encoded claims
            tweetIndex {list} -- the corresponding tweet index

        Keyword Arguments:
            num {int} -- the number of top N (default: {10})

        Returns:
            defaultdict(list) -- {claimID: [sentence, score, tweetIndex]}
        """

        claims2tweets = defaultdict(list)
        scores = sd.cdist(encodedSentences, encodedClaims, "cosine")
        # sorted_ids = np.argsort(scores)
        maxClaimIDs = np.argmin(scores, axis=1)
        for index, maxClaimID in enumerate(maxClaimIDs):
            claims2tweets[np.asscalar(maxClaimID)].append(
                (sentences[index],
                 scores[index][np.asscalar(maxClaimID)],
                 tweetIndex[index]))
        # for claimID, sentInfos in claims2tweets.items():
        #     print("Sentence:")
        #     print("", claims[claimID])
        #     print("\nNearest neighbors:")
        #     for sent, score, twIndx in sentInfos:
        #         print(" %s (%.3f) %d" %
        #               (sent, score, twIndx))
        return claims2tweets

    # def getSimilarClaims(self, claims, tweets):
    #     """Get similar claims.

    #     Arguments:
    #         claims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
    #         tweets {list} -- a list of tweets

    #     Returns:
    #         list -- [claim1, claim2, ...]
    #     """
    #     # tweetID_675 = None
    #     # tweetID_14 = None
    #     # tweetID_956 = None
    #     # for index, item in enumerate(claims):
    #     #     if item[0] == 675:
    #     #         print("index of tweetID 675 ", index)
    #     #         tweetID_675 = index
    #     #     if item[0] == 14:
    #     #         print("index of tweetID 14 ", index)
    #     #         tweetID_14 = index
    #     #     if item[0] == 956:
    #     #         print("index of tweetID 956 ", index)
    #     #         tweetID_956 = index
    #     #     if tweetID_675 and tweetID_14 and tweetID_956:
    #     #         break

    #     claimsContent = [claim[3] for claim in claims]
    #     # encodedClaims = [self.encodeSen([cc]) for cc in claimsContent]
    #     # encodedClaims_numpy = np.concatenate(encodedClaims)
    #     encodedClaims = self.encodeSen(claimsContent)

    #     # scores = sd.cdist(encodedClaims_numpy, encodedClaims_numpy, "cosine")
    #     scores = sd.cdist(encodedClaims, encodedClaims, "cosine")
    #     similarClaimsIndeices = np.argwhere(scores < 0.5)

    #     # test = [claimsContent[tweetID_675],
    #     #         claimsContent[tweetID_14], claimsContent[tweetID_956]]
    #     # encodedtest = self.encodeSen(test)
    #     # scores_test = sd.cdist(encodedtest, encodedtest, "cosine")
    #     # print("test ", scores_test)

    #     # print(encodedtest[0])
    #     # print(encodedClaims[tweetID_675])

    #     # print("657 ", np.array_equal(
    #     #     encodedtest[0], encodedClaims[tweetID_675]))
    #     # print("14 ", np.array_equal(encodedtest[1], encodedClaims[tweetID_14]))
    #     # print("956 ", np.array_equal(
    #     #     encodedtest[2], encodedClaims[tweetID_956]))

    #     # print("tweetID_675: claims index {} {}".format(
    #     #     tweetID_675, claimsContent[tweetID_675]))
    #     # print("pair indexes lower than 0.5 {}".format(
    #     #     np.argwhere(scores[tweetID_675] < 0.5).tolist()))

    #     # tmp_675 = np.argwhere(scores[tweetID_675] < 0.5).tolist()
    #     # print("original claim {}".format(claimsContent[tweetID_675]))
    #     # for t in tmp_675:
    #     #     print("claim {} score {}".format(
    #     #         claimsContent[t[0]], scores[tweetID_675][t[0]]))

    #     # print("tweetID_14: claims index {} {}".format(
    #     #     tweetID_14, claimsContent[tweetID_14]))
    #     # print("pair indexes lower than 0.5 {}".format(
    #     #     np.argwhere(scores[tweetID_14] < 0.5).tolist()))

    #     # tmp_14 = np.argwhere(scores[tweetID_14] < 0.5).tolist()
    #     # print("original claim {}".format(claimsContent[tweetID_14]))
    #     # for t in tmp_14:
    #     #     print("claim {} score {}".format(
    #     #         claimsContent[t[0]], scores[tweetID_14][t[0]]))

    #     similarClaimsIndeicesComponents = Utility.Helper.getConnectedComponents(
    #         similarClaimsIndeices.tolist())
    #     similarClaimsComponents = defaultdict(list)
    #     similarClaims = defaultdict(int)
    #     for component in similarClaimsIndeicesComponents:
    #         tweet2features = defaultdict(int)
    #         for index in component:
    #             tweetID = claims[index][0]
    #             text = claims[index][3]
    #             features = tweets[tweetID].reply + \
    #                 tweets[tweetID].retweets + \
    #                 tweets[tweetID].favorites + 1
    #             tweet2features[text] += features
    #         sortedTweet2Number = Utility.PreprocessData.sortDict(
    #             tweet2features)
    #         similarClaimsComponents[sortedTweet2Number[0][0]] = list(component)
    #         componentFeatures = [feature for text,
    #                              feature in sortedTweet2Number]
    #         similarClaims[sortedTweet2Number[0][0]] = sum(
    #             componentFeatures) / len(componentFeatures)
    #     sortedSimilarClaims = Utility.PreprocessData.sortDict(
    #         similarClaims)
    #     return similarClaimsComponents, sortedSimilarClaims

    def getClusteredClaims(self, claims, tweets, eps):
        """Get clusters of the claims by DBSCAN.

        Arguments:
            claims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
            tweets {list} -- a list of tweets

        Returns:
            tuple -- (cluster2claimsIndexes, cluster2coreSampleIndices)
        """
        cluster2claimsIndexes = defaultdict(list)
        claimsContent = [claim[4].lower() for claim in claims]
        encodedClaims = self.model.encodeSen(claimsContent)
        # scores = sd.cdist(encodedClaims, encodedClaims, "cosine")

        # db = DBSCAN(eps=0.45, min_samples=2, metric="precomputed").fit(scores)
        print("eps for DBSCAN is ", eps)
        db = DBSCAN(eps=eps, min_samples=2,
                    metric="cosine").fit(encodedClaims)
        labels = db.labels_.tolist()

        for index, label in enumerate(labels):
            cluster2claimsIndexes[str(label)].append(index)

        # print("labels ", labels)
        # print("core_sample_indices ", db.core_sample_indices_.tolist())

        # print(cluster2claimsIndexes)
        self.helper.dumpJson(
            self.fileFolderPath, "cluster_to_claims_indexes.json",
            cluster2claimsIndexes)
        print("cluster_to_claims_indexes.json has been saved.")

        cluster2coreSampleIndices = defaultdict(list)
        coreSampleIndices = db.core_sample_indices_.tolist()
        for coreSampleIndex in coreSampleIndices:
            clusterLabel = labels[coreSampleIndex]
            cluster2coreSampleIndices[str(
                clusterLabel)].append(coreSampleIndex)

        self.helper.dumpJson(
            self.fileFolderPath, "cluster_to_core_sample_indices.json",
            cluster2coreSampleIndices)
        print("cluster_to_core_sample_indices.json has been saved.")
        # for key, value in cluster2claimsIndexes.items():
        #     print("=" * 100)
        #     print("cluster {}".format(key))
        #     for v in value:
        #         cluster2claimsContents[key].append(claimsContent[v])
        #         print(claimsContent[v])
        return cluster2claimsIndexes, cluster2coreSampleIndices

    # def rankClusteredClaims(self, cluster2claimsIndexes, claims):
    #     for label, claimIndexes in cluster2claimsIndexes.items():

    def rankClusteredClaims(self, cluster2claimsIndexes, cluster2coreSampleIndices, claims, fullClaims, tweets):
        """Rank claims in clusters.

        Arguments:
            cluster2claimsIndexes {dict} -- {cluster1: [claim1Index, claim2Index, ...], ...}
            cluster2coreSampleIndices {dict} -- {cluster1: [coreSampleIndex, ...], ...}
            claims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
            tweets {list} -- a list of tweets
        Returns:
            list -- [(representativeClaim1, feature), (representativeClaim2, features), ...]
        """
        representativeClaim2ClaimsCluster = defaultdict(list)
        representativeClaim2FullClaimsCluster = defaultdict(list)
        representativeClaim2ClusterFeatures = defaultdict(float)
        representativeClaim2Subject = defaultdict(int)

        tweetID2Info = self.helper.loadJson(
            self.fileFolderPath+"/tweets_id2Info.json")

        for label, claimIndexes in cluster2claimsIndexes.items():
            flag = False
            label = int(label)
            if label == -1:
                # flag = True
                continue
            tweet2features, tweet2date, tweet2rumor = self.__getFeature4Claims(
                claimIndexes, claims, tweets)
            sortedTweet2Number = Utility.PreprocessData.sortDict(
                tweet2features)
            coreTweet2features, _, _ = self.__getFeature4Claims(
                cluster2coreSampleIndices[str(label)], claims, tweets)
            sortedCoreTweet2Number = Utility.PreprocessData.sortDict(
                coreTweet2features)
            representativeClaim = sortedCoreTweet2Number[0][0]

            self.__getClusterClaimsAndSubject(
                representativeClaim, claimIndexes,
                claims, fullClaims, tweetID2Info,
                representativeClaim2ClaimsCluster,
                representativeClaim2FullClaimsCluster,
                representativeClaim2Subject,
                tweet2date, tweet2rumor, flag)
            self.__getFeature4Cluster(
                sortedTweet2Number,
                representativeClaim,
                representativeClaim2ClusterFeatures, flag)

        self.helper.dumpJson(
            self.fileFolderPath,
            "representative_claim_to_claims_cluster.json",
            representativeClaim2ClaimsCluster)
        print("representative_claim_to_claims_cluster.json has been saved.")

        self.helper.dumpJson(
            self.fileFolderPath,
            "representative_claim_to_full_claims_cluster.json",
            representativeClaim2FullClaimsCluster)
        print("representative_claim_to_full_claims_cluster.json has been saved.")

        self.helper.dumpJson(
            self.fileFolderPath,
            "representative_claim_to_subject.json",
            representativeClaim2Subject)
        print("representative_claim_to_subject.json has been saved.")

        self.helper.dumpJson(
            self.fileFolderPath,
            "representative_claim_to_cluster_feature.json",
            representativeClaim2ClusterFeatures)
        print("representative_claim_to_cluster_feature.json has been saved.")

        rankedClusterClaims = Utility.PreprocessData.sortDict(
            representativeClaim2ClusterFeatures)
        self.helper.dumpJson(self.fileFolderPath,
                             "ranked_cluster_claims.json",
                             rankedClusterClaims)
        print("ranked_cluster_claims.json has been saved.")
        return rankedClusterClaims

    def __getClusterClaimsAndSubject(self, representativeClaim, claimIndexes,
                                     claims, fullClaims, tweetID2Info,
                                     representativeClaim2ClaimsCluster,
                                     representativeClaim2FullClaimsCluster,
                                     representativeClaim2Subject,
                                     tweet2date, tweet2rumor, flag):
        """Get representative claim for each cluster.

        Arguments:
            sortedCoreTweet2Number {list} -- [(coreTweet, feature), ...]
            claimIndexes {list} -- [claimIndex1, claimIndex2, ...]
            claims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
            representativeClaim2ClaimsCluster {dict} -- {claim: [claim1, claim2, ...], ...}
            flag {boolean} -- flag for label: -1
        """
        claimsContent = [(claims[index][4], tweet2date[claims[index][4]],
                          tweet2rumor.get(claims[index][4]))
                         for index in claimIndexes]
        fullClaimsContent = [
            (fullClaims[index][4], tweet2date[claims[index][4]],
             tweet2rumor.get(claims[index][4])) for index in claimIndexes]
        for index in claimIndexes:
            if claims[index][4] == representativeClaim:
                tweetID = str(claims[index][0])
                subjectIndex = int(claims[index][1]) - 1
                subject = tweetID2Info[tweetID][subjectIndex][1]
                representativeClaim2Subject[representativeClaim] = subject
        if not flag:
            representativeClaim2ClaimsCluster[representativeClaim] = claimsContent[:]
            representativeClaim2FullClaimsCluster[representativeClaim] = fullClaimsContent[:]
        else:
            for cc in claimsContent:
                representativeClaim2ClaimsCluster[cc] = cc

    def __getFeature4Claims(self, claimIndexes, claims, tweets):
        """Get feature for claims.

        Arguments:
            claimIndexes {list} -- [claimIndex1, claimIndex2, ...]
            claims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
            tweets {list} -- a list of tweets
        Returns:
            dict -- {tweet: feature, ...}
        """
        tweet2features = defaultdict(int)
        tweet2date = defaultdict(str)
        tweet2rumor = defaultdict(bool)
        for claimIndex in claimIndexes:
            tweetID = claims[claimIndex][0]
            text = claims[claimIndex][4]
            features = tweets[tweetID].reply + \
                tweets[tweetID].retweets + \
                tweets[tweetID].favorites + 1
            tweet2features[text] += features
            tweet2date[text] = tweets[tweetID].date.strftime(
                '%Y-%m-%d %H:%M:%S')
            if hasattr(tweets[tweetID], 'rumor'):
                tweet2rumor[text] = tweets[tweetID].rumor
        return tweet2features, tweet2date, tweet2rumor

    def __getFeature4Cluster(self, sortedTweet2Number, representativeClaim,
                             representativeClaim2ClusterFeatures, flag):
        """Get feature for each cluster.

        Arguments:
            sortedTweet2Number {list} -- [(tweet, feature), ...]
            representativeClaim2ClusterFeatures {dict} -- {claim: feature, ...}
            flag {boolean} -- flag for label: -1
        """
        if not flag:
            clusterFeatures = [feature for text, feature in sortedTweet2Number]
            representativeClaim2ClusterFeatures[representativeClaim] = sum(
                clusterFeatures) / len(clusterFeatures)
        else:
            for text, feature in sortedTweet2Number:
                representativeClaim2ClusterFeatures[text] = feature

    def getSimilarNews(self, claim, news):
        """Get similar news to the claim.

        Arguments:
            claim {str} -- representative claim for each cluster
            news {list} -- a list of news got by NewsAPI

        Returns:
            str -- the most similar new
        """
        encodedClaim = self.model.encodeSen([claim])
        encodedNews = self.model.encodeSen(news)
        scores = sd.cdist(encodedClaim, encodedNews, "cosine")
        print("scores ", scores)
        similarNewID = np.asscalar(np.argmin(scores, axis=1))
        print("similarNewID ", similarNewID)
        similarNew = news[similarNewID]
        return similarNew
