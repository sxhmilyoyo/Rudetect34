import CMUTweetTagger
import Utility
import os
from collections import defaultdict
from tweebo_parser import API, ServerError
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


class ClaimExtractor(object):
    """Extract the claims.

    Using the CMU TweetNLP ark-tweet-nlp-python wrapper.
    """

    def __init__(self, rootpath="", folderpath=""):
        self.helper = Utility.Helper(rootpath)
        self.preprocessData = Utility.PreprocessData(rootpath)
        self.rootpath = rootpath
        self.folderpath = folderpath
        self.fileFolderPath = os.path.join(
            self.rootpath, self.folderpath, "final")
        self.termination = set([".", "!"])

    def __tag(self, cleanedTweets):
        """Tag the cleaned tweets.

        Arguments:
            cleanedTweets {list} -- a list of cleaned tweets

        Returns:
            list -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]
        """
        print("The number of tweets before tagged {}".format(len(cleanedTweets)))
        taggedTweets = CMUTweetTagger.runtagger_parse(cleanedTweets)
        print("The number of tweets after tagged {}".format(len(taggedTweets)))
        self.helper.dumpJson(
            self.fileFolderPath, "tagged_tweets.json", taggedTweets)
        print("tagged_tweets.json has been saved.")
        return taggedTweets

    def __mergeNoun(self, taggedTweets):
        """Merge the adjacent word with Noun Pos Tag.

        Noun with the POS tags: N, ^, S
        Arguments:
            taggedTweets {list} -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]

        Returns:
            newMergedTaggedTweets -- [[(form, pos, score), ...], [(form, pos, score), ...], ...]
        """
        newMergedTaggedTweets = []
        for taggedTweet in taggedTweets:
            index = 0
            newMergedTaggedTweet = []
            # print("length of tweet ", len(taggedTweet))
            # for i in range(index, len(taggedTweet)):
            while index < len(taggedTweet):
                merge = list(taggedTweet[index])
                if merge[1] in set(["N", "^", "S"]):
                    j = index + 1
                    while j < len(taggedTweet):
                        if taggedTweet[j][1] in set(["N", "^", "S"]):
                            merge[0] = merge[0] + " " + taggedTweet[j][0]
                            merge[1] = "N"
                            merge[2] = (merge[2] + taggedTweet[j][-1]) / 2
                            j += 1
                        else:
                            index = j
                            # print("index is ", index)
                            break
                    index = j
                else:
                    index += 1
                newMergedTaggedTweet.append(tuple(merge))
            newMergedTaggedTweets.append(newMergedTaggedTweet)
        self.helper.dumpJson(
            self.fileFolderPath,
            "merged_noun_tagged_tweets.json",
            newMergedTaggedTweets)
        print("merged_noun_tagged_tweets.json has been saved.")
        return newMergedTaggedTweets

    def extractNoun(self, cleanedTweets):
        """Extract the Noun in merged Noun tagged cleaned tweets.

        Noun with the POS tags: N, ^, S
        Arguments:
            tweets {list} -- the list of cleaned tweets
        Returns:
            noun2number -- {noun1: num1, noun2: num2, ...}
        """
        taggedTweets = self.__tag(cleanedTweets)
        mergedNounTweets = self.__mergeNoun(taggedTweets)
        noun2number = defaultdict(int)
        nounPOSTags = set(["N", "^", "S"])
        for mergedNounTweet in mergedNounTweets:
            for word, posTag, score in mergedNounTweet:
                if posTag in nounPOSTags:
                    noun2number[word] += 1
        self.helper.dumpJson(self.fileFolderPath,
                             "noun2number.json", noun2number)
        print("noun2number.json has been saved.")
        sortedNoun2Number = self.preprocessData.sortDict(noun2number)
        self.helper.dumpJson(self.fileFolderPath,
                             "sorted_noun2number.json",
                             sortedNoun2Number)
        print("sorted_noun2number.json has been saved.")
        return noun2number

    def __callTweeboParser(self, cleanedTweets):
        """Parse the cleaned tweets by TweeboParser Python API.

        Arguments:
            cleanedTweets {list} -- the list of cleaned tweets
        Returns:
            result_conll -- [r1, r2, ...]
        """
        tweebo_api = API()
        try:
            result_conll = tweebo_api.parse_conll(cleanedTweets)
        except ServerError as e:
            print(f'{e}\n{e.message}')
        result_conll_terms = [r.split("\n") for r in result_conll]
        return result_conll_terms

    def __splitResult(self, tweet):
        """Split the CoNLL format result.

        Arguments:
            tweet {list} -- [info_term1, info_term2, ...]
        """
        for term in tweet:
            if len(term) > 0:
                parts = term.split("\t")
                idx = parts[0]
                form = parts[1]
                lemma = parts[2]
                upostag = parts[3]
                xpostag = parts[4]
                feats = parts[5]
                head = parts[6]
                deprel = parts[7]
                # if deprel != "_" and deprel != "CONJ" and deprel != "MWE":
                # print(deprel)
                deps = parts[8]
                misc = parts[9]

                yield idx, form, lemma, upostag, xpostag, feats, head, deprel, deps, misc

    def __parse(self, cleanedTweets):
        """Parse the cleaned tweets by TweeboParser Python API.

        Arguments:
            cleanedTweets {list} -- a list of cleaned tweet

        Returns:
            dict -- {tweet_id: [(info_term1), (info_term2), ...], ...}
        """
        result_conll_terms = self.__callTweeboParser(cleanedTweets)
        result = defaultdict(list)
        for tweet_id, result_conll_term in enumerate(result_conll_terms):
            result[tweet_id] = [
                x for x in self.__splitResult(result_conll_term)]
        self.helper.dumpJson(self.fileFolderPath,
                             "tweets_id2Info.json", result)
        print("tweets_id2Info.json has been saved.")
        return result

    def __findVerbRoot(self, parsedTweet):
        """Find verb root index and id in the sentence.

        Root is the term with HEAD is 0.
        Arguments:
            parsedTweet {list} -- [(term1_info), (term2_info), ...]

        Returns:
            list -- [(index1(int), id1(str)), (index2(int), id2(str)), ...]
        """
        verbRootIndex = []
        for index, term in enumerate(parsedTweet):
            if int(term[6]) == 0 and term[3] == "V":
                verbRootIndex.append((index, term[0]))
        return verbRootIndex

    def __findBeginning(self, parsedTweet, end):
        """Find the begining index of the current sentence.

        Arguments:
            parsedTweet {list} -- [(term1_info), (term2_info), ...]
            end {int} -- the index of the end

        Returns:
            int -- the index of the sentence start
        """
        if end == 0:
            return 0
        else:
            start = end - 1
        while start > 0:
            if parsedTweet[start][3] == ",":
                return start + 1
            else:
                start -= 1
        return 0

    def __mergeNounasSubject(self, tweets, parsedTweets):
        """Merge the adjacent word with Noun Pos Tag as Subject in TweeboParser.

        Noun with the POS tags: N, ^, S
        Arguments:
            tweets {list} -- the list of tweet
            parsedTweets {dict} -- {tweet_id: [(term1_info), (term2_info), ()], ...}

        Returns:
            mergedNoun -- {tweet_id: [noun1, noun2, ...], ...}
        """
        mergedNoun = defaultdict(list)
        for tweetID, parsedTweet in parsedTweets.items():
            verbRootIndices = self.__findVerbRoot(parsedTweet)
            if len(verbRootIndices) == 0:
                continue

            for verbRootIndex, verbRootID in verbRootIndices:
                sentStart = self.__findBeginning(parsedTweet, verbRootIndex)
                start = sentStart

                # print("length of tweet ", len(taggedTweet))
                # for i in range(index, len(taggedTweet)):
                while start < len(parsedTweet) and start < verbRootIndex:
                    merge = list(parsedTweet[start])
                    if merge[3] in set(["N", "^", "S"]) and int(merge[6]) == int(verbRootID):
                        j = start + 1
                        while j < len(parsedTweet) and j < verbRootIndex:
                            if parsedTweet[j][3] in set(["N", "^", "S"]) and int(parsedTweet[j][6]) == int(verbRootID):
                                merge[1] = merge[1] + " " + parsedTweet[j][1]
                                j += 1
                            else:
                                # print("index is ", index)
                                break
                        # find dependencyNoun as final subject
                        subjects = self.__findDependencyNoun(
                            parsedTweet, sentStart, start-1, merge, tweets, tweetID)
                        if type(subjects[0]) is list:
                            subject = subjects[-1]
                        else:
                            subject = subjects
                        subject[3] = "N"
                        subject[7] = "NSUBJ"
                        start = j + 1
                        mergedNoun[tweetID].append(subject)
                    else:
                        start += 1
        self.helper.dumpJson(
            self.fileFolderPath,
            "merged_noun_as_subject.json",
            mergedNoun)
        print("merged_noun_as_subject.json has been saved.")
        return mergedNoun

    def __findDependencyNoun(self, parsedTweet, sentStart, start, currentParsedTerm, tweets, tweetID):
        """Find the previous noun dependent on current noun.

        Arguments:
            parsedTweet {list} -- [(term1_info), (term2_info), ()]
            sentStart {int} -- the beginning index of the sentence
            start {int} -- the index of the start
            currentParsedTerm {tuple} -- the term info
            tweets {list} -- the list of tweets
            tweetID {int} -- the id of the tweet

        Returns:
            list -- [description]
        """
        currentNounID = int(currentParsedTerm[0])
        candidateDependencyNoun = []
        while start >= sentStart:
            if parsedTweet[start][3] in set(["N", "^", "S"]) and int(parsedTweet[start][6]) == currentNounID:
                parsedTweetList = list(parsedTweet[start])
                parsedTweetList[6] = currentParsedTerm[6]
                candidateDependencyNoun.append(parsedTweetList)
            elif int(parsedTweet[start][6]) == currentNounID and parsedTweet[start][3] == "D" and parsedTweet[start][1].lower() in set(["this", "that", "those", "these"]):
                # find the hashtag in this tweet for pronoun like "this, those", except "the"
                hashtags = tweets[tweetID].hashtags.split()
                if hashtags:

                    noSymbolHashtag = re.sub("([#])", "", hashtags[0])
                    parsedTweetList = list(parsedTweet[start])
                    parsedTweetList[1] = noSymbolHashtag
                    parsedTweetList[6] = currentParsedTerm[6]
                    candidateDependencyNoun.append(parsedTweetList)
                    break
            start -= 1
        if candidateDependencyNoun:
            return candidateDependencyNoun
        return currentParsedTerm

    def collectSubject(self, tweets, cleanedTweets):
        """Collect the information of subject in tweets.

        Information includes: number, corresponded tweet id and its index.
        Noun with the POS tags: N, ^, S and HEAD is 0.
        Arguments:
            tweets {list} -- the list of tweets
            cleanedTweets {list} -- the list of cleaned tweets
        Returns:
            mergedNoun -- {tweet_id: [noun1, noun2, ...], ...}
            subject2number -- {subject1: num1, subject2: num2, ...}
            subject2tweetInfo -- {subject1: (tweet id(str), subjectId(str)), subject2: (tweet id(str), subjectId(str)), ...}
            parsedTweets -- {tweet_id: [(info_term1), (info_term2), ...], ...}            
        """
        subject2number = defaultdict(int)
        subject2tweetInfo = defaultdict(list)
        parsedTweets = self.__parse(cleanedTweets)
        mergedNoun = self.__mergeNounasSubject(tweets, parsedTweets)
        for tweetID, nounsInfo in mergedNoun.items():
            for nounInfo in nounsInfo:
                subject2number[nounInfo[1].lower()] += 1
                subject2tweetInfo[nounInfo[1].lower()].append(
                    (tweetID, nounInfo[0]))

        self.helper.dumpJson(self.fileFolderPath,
                             "subject2number.json", subject2number)
        print("subject2number.json has been saved.")
        sortedSubject2Number = self.preprocessData.sortDict(subject2number)
        self.helper.dumpJson(self.fileFolderPath,
                             "sorted_subject2number.json",
                             sortedSubject2Number)
        print("sorted_subject2number.json has been saved.")
        self.helper.dumpJson(self.fileFolderPath,
                             "subject2tweetInfo.json", subject2tweetInfo)
        print("subject2tweetInfo.json has been saved.")
        return mergedNoun, sortedSubject2Number, subject2tweetInfo, parsedTweets

    def getCandidateClaims(self, tweets, mergedNoun, sortedSubject2Number, subject2tweetInfo, parsedTweets, top=3):
        """Get candidate claims from tweets based on subject.

        Arguments:
            tweets {list} -- the list of tweets
            mergedNoun {dict} -- {tweet_id: [noun1, noun2, ...], ...}
            sortedNoun2Number {list} -- [[subject1, number], ...]
            subject2tweetInfo {dict} -- {subject1: (tweet id(str), subjectId(str)), subject2: (tweet id(str), subjectId(str)), ...}
            parsedTweets {dict} -- {tweet_id: [(info_term1), (info_term2), ...], ...}
            top {int} -- the number of top subjects to be analyzed
        Returns:
            dict -- {subject1: [claim1, claim2, ...], ...}
        """
        candidateClaims = defaultdict(list)
        for subject, _ in sortedSubject2Number[:top]:
            print("subject is {}".format(subject))
            for tweetID, subjectId in subject2tweetInfo[subject]:
                # get edited parsed term

                subjectId = int(subjectId)
                # original parsed tweet
                parsedTweet = parsedTweets[tweetID]
                # Id is bigger than index by one
                startSent = self.__findBeginning(parsedTweet, subjectId-1)
                totalLen = len(parsedTweet)

                rootIndex, sub, verb = self.__getSubVerb(
                    mergedNoun, tweetID, subjectId, parsedTweet)
                rootID = rootIndex+1
                startIndex = rootIndex + 1
                objects = self.__getObject(
                    startIndex, totalLen, parsedTweet, rootID, tweetID, startSent, tweets)
                # claimInfo: tweet id, claim

                if objects or (objects == [] and verb not in set(["is", "was", "are", "were", "be"])):
                    claimInfo = (tweetID, " ".join([sub, verb]+objects))
                    candidateClaims[subject].append(claimInfo)
        self.helper.dumpJson(self.fileFolderPath,
                             "candidateClaims.json", candidateClaims)
        print("candidateClaims.json has been saved.")
        # find similar subjects
        return candidateClaims

    def mergeSimilarSubjects(self, candidateClaims):
        """Merge similar subjects and their corresponding claims.

        Arguments:
            candidateClaims {dict} -- {subject: [claim1, claim2, ...], ...}

        Returns:
            dict -- {subject: [claim1, claim2, ...], ...}
        """
        subjects = list(candidateClaims.keys())
        similarSubjects = defaultdict(list)
        mergedCandidateClaims = defaultdict(list)
        while subjects:
            temp = subjects.pop(0)
            for s in subjects:
                if fuzz.partial_ratio(temp, s) == 100:
                    similarSubjects[temp].append(s)
            for s in similarSubjects[temp]:
                subjects.pop(subjects.index(s))
        for subject in similarSubjects.keys():
            mergedCandidateClaims[subject] = candidateClaims[subject]
            if similarSubjects[subject]:
                for similarSubject in similarSubjects[subject]:
                    mergedCandidateClaims[subject] += candidateClaims[similarSubject]
        self.helper.dumpJson(
            self.fileFolderPath, "mergedCandidateClaims.json", mergedCandidateClaims)
        print("mergedCandidateClaims.json has been saved.")

        return mergedCandidateClaims

    def __getSubVerb(self, mergedNoun, tweetID, subjectId, parsedTweet):
        """Get subject and verb based on subjectId.

        Arguments:
            mergedNoun {dict} -- {tweet_id: [noun1, noun2, ...], ...}
            tweetID {int} -- the tweet ID
            subjectId {int} -- the subject ID
            parsedTweet {list} -- [(term_info1), (term_info2), ...]

        Returns:
            tuple -- (root index, subject, verb)
        """
        nouns = mergedNoun[tweetID]
        for noun in nouns:
            if int(noun[0]) == int(subjectId):
                break
        subject = noun[1]
        rootID = int(noun[6])
        rootIndex = rootID - 1
        verb = parsedTweet[rootIndex][1]
        return rootIndex, subject, verb

    def __getObject(self, startIndex, totalLen, parsedTweet, rootID, tweetID, startSent, tweets):
        """Get Object from start index.

        Arguments:
            startIndex {int} -- the start index
            totalLen {int} -- the total length of the tweet
            parsedTweet {list} -- [description]
            rootID {int} -- root ID
            tweetID {int} -- tweet ID
            startSent {int} -- the start index of the current sentence
            tweets {list} -- the list of tweets

        Returns:
            list -- the list of objects
        """
        objects = []
        while startIndex < totalLen:
            parsedTerm = parsedTweet[startIndex]
            if parsedTerm[3] == "," and parsedTerm[1] in self.termination:
                break
            if int(parsedTerm[6]) == rootID:
                if parsedTerm[3] == "V":
                    # add second verb
                    objects.append(parsedTerm[1])
                    nounInfo = self.__findNoun(
                        startIndex+1, parsedTerm, parsedTweet)
                    if not nounInfo:
                        print("breaking tweet id is {}".format(tweetID))
                        break
                    dependencyNounInfos = self.__findDependencyNoun(
                        parsedTweet, startSent, int(nounInfo[0])-1-1, nounInfo, tweets, tweetID)
                    if type(dependencyNounInfos) is list:
                        while dependencyNounInfos:
                            # add dependency noun
                            objects.append(
                                dependencyNounInfos.pop()[1])
                    # add noun
                    objects.append(nounInfo[1])
                    break
                elif parsedTerm[3] in set(["N", "^", "S"]):
                    dependencyNounInfos = self.__findDependencyNoun(
                        parsedTweet, startSent, startIndex-1, parsedTerm, tweets, tweetID)
                    if dependencyNounInfos is list:
                        while dependencyNounInfos:
                            # add dependency noun
                            objects.append(
                                dependencyNounInfos.pop()[1])
                    # add noun
                    objects.append(parsedTerm[1])
                    break
                elif parsedTerm[3] == "A":
                    # add adj
                    objects.append(parsedTerm[1])
                    break
            startIndex += 1
        return objects

    def __findNoun(self, startIndex, currentParsedTerm, parsedTweet):
        """Find noun dependent on currentParsedTerm from startIndex.

        Arguments:
            startIndex {int} -- the beginning index
            currentParsedTerm {tuple} -- the current term info
            parsedTweet {list} -- [(term_info1), (term_info2), ...]

        Returns:
            tuple -- parsed term
        """
        while startIndex < len(parsedTweet):
            if parsedTweet[startIndex][3] in set(["S", "N", "^"]) and int(parsedTweet[startIndex][6]) == int(currentParsedTerm[0]):
                return parsedTweet[startIndex]
            startIndex += 1
        return None

    def __findDependencyonSubject(self, startSent, subjectId, parsedTweet):
        """Find the index of the leftmost term dependent on subject.

        Arguments:
            startSent {int} -- the beginning index of the current sentence
            subjectId {int} -- the id of the subject
            parsedTweet {list} -- [(info_term1), (info_term2), ...]

        Returns:
            int -- the index of the leftmost term dependent on subject
        """
        start = startSent
        # Id is bigger than index by one
        while start < (subjectId-1):
            head = int(parsedTweet[start][6])
            if head == subjectId:
                return start
            start += 1
        return subjectId-1

    def rankClaims(self, initQuery, tweets, candidateClaims, top=5):
        """Rank candidate claims.

        Arguments:
            initQuery {str} -- the initial query
            tweets {list} -- the list of tweets
            candidateClaims {dict} -- {subject1: [claim1, claim2, ...], ...}
            top {int} -- the number of top claims

        Returns:
            dict -- {subject1: [claim1, claim2, ...], ...}
        """
        subjects = list(candidateClaims.keys())
        relatedSubjects = process.extract(initQuery, subjects)
        finalSubjects = [sub for sub, score in relatedSubjects if score >= 50]
        subject2claimFeature = defaultdict(dict)
        subject2rankedClaims = defaultdict(list)
        for subject in finalSubjects:
            print("subject is {}".format(subject))
            claimIndex2feature = defaultdict(int)
            candidateClaims4Subject = candidateClaims[subject]
            for claimIndex, claimInfo in enumerate(candidateClaims4Subject):
                tweetIndex = int(claimInfo[0])
                tweet = tweets[tweetIndex]
                # print("claim is {}".format(claimInfo[1]))
                # print("tweet is {}".format(tweet.text))
                # print("tweet's permalink is {}".format(tweet.permalink))
                feature = tweet.reply + tweet.retweets + tweet.favorites
                claimIndex2feature[claimIndex] = feature
            subject2claimFeature[subject] = claimIndex2feature
            sortedClaimIndex2feature = self.preprocessData.sortDict(
                claimIndex2feature)
            for claimIndex, _ in sortedClaimIndex2feature[:top]:
                subject2rankedClaims[subject].append(
                    candidateClaims4Subject[claimIndex])

        self.helper.dumpJson(self.fileFolderPath,
                             "claimIndex2feature.json", subject2claimFeature)
        print("subject2claimFeature.json has been saved.")
        self.helper.dumpJson(self.fileFolderPath,
                             "subject2rankedClaims.json", subject2rankedClaims)
        print("subject2rankedClaims.json has been saved.")
        return subject2rankedClaims
