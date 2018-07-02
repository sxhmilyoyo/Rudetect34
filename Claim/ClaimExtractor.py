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
        self.termination = set([".", "!", "..."])

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
            newMergedTaggedTweets -- \
                [[(form, pos, score), ...], [(form, pos, score), ...], ...]
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
            if tweetID == 71:
                print("71 ", verbRootIndices)
            if len(verbRootIndices) == 0:
                continue

            for verbRootIndex, verbRootID in verbRootIndices:
                sentStart = self.__findBeginning(parsedTweet, verbRootIndex)
                start = sentStart

                # print("length of tweet ", len(taggedTweet))
                # for i in range(index, len(taggedTweet)):
                while start < len(parsedTweet) and start < verbRootIndex:
                    merge = list(parsedTweet[start])
                    if int(merge[6]) == int(verbRootID) and \
                            (merge[3] in set(["N", "^", "S", "G"])
                             or (merge[1].lower()
                                 in set(["where", "who", "what", "how", "when", "why"]))):
                        # find after
                        j = start + 1
                        while j < len(parsedTweet) and j < verbRootIndex:
                            if parsedTweet[j][3] in set(["N", "^", "S"]) and int(parsedTweet[j][6]) == int(verbRootID):
                                if merge[1].lower() in set(["where", "who", "what", "how", "when", "why"]):
                                    merge = list(parsedTweet[j])
                                    start = j
                                else:
                                    merge[1] = merge[1] + \
                                        " " + parsedTweet[j][1]
                            j += 1
                            # else:
                            #     # print("index is ", index)
                            #     break
                        # find dependencyNoun as final subject
                        # find previously
                        subject = self.__findDependencyNoun(
                            parsedTweet, sentStart, start-1, merge, tweets, tweetID)
                        # if type(subjects[0]) is list:
                        #     subject = subjects[-1]
                        # else:
                        #     subject = subjects
                        subject[3] = "N"
                        subject[7] = "NSUBJ"
                        # start = j + 1
                        mergedNoun[tweetID].append(subject)
                        break
                    # handle "G" subject
                    elif int(merge[6]) == 0 and merge[3] == "G" and abs(int(merge[0])-int(verbRootID)) == 1:
                        merge[6] = verbRootID
                        subject = self.__findDependencyNoun(
                            parsedTweet, sentStart, start-1, merge, tweets, tweetID)
                        subject[3] = "N"
                        subject[7] = "NSUBJ"
                        mergedNoun[tweetID].append(subject)
                        start += 1
                    else:
                        start += 1
        self.helper.dumpJson(
            self.fileFolderPath,
            "merged_noun_as_subject.json",
            mergedNoun)
        print("merged_noun_as_subject.json has been saved.")
        return mergedNoun

    def __findDependencyNoun(self, parsedTweet, sentStart, start, currentParsedTerm, tweets, tweetID):
        """Find the previous noun or adjective dependent on current noun.

        Arguments:
            parsedTweet {list} -- [(term1_info), (term2_info), ()]
            sentStart {int} -- the beginning index of the sentence
            start {int} -- the index of the start
            currentParsedTerm {tuple} -- the term info
            tweets {list} -- the list of tweets
            tweetID {int} -- the id of the tweet

        Returns:
            list -- parsed term
        """
        currentParsedList = list(currentParsedTerm)
        currentNounID = int(currentParsedTerm[0])
        # candidateDependencyNoun = []
        preParsedTweetList = None
        while start >= sentStart:
            if parsedTweet[start][3] in set(["N", "^", "S", "A", "$", "O", "G"]) and int(parsedTweet[start][6]) == currentNounID:
                # parsedTweetList = list(parsedTweet[start])
                # parsedTweetList[6] = currentParsedTerm[6]
                # parsedTweetList[-1] = parsedTweetList[1] + currentParsedTerm[1]
                # currentParsedList[1] = parsedTweet[start][1] + \
                #     " " + currentParsedList[1]
                # if preParsedTweetList:
                #     parsedTweetList[-1] = parsedTweetList[1] + \
                #         " " + preParsedTweetList[-1]
                # else:
                #     parsedTweetList[-1] = parsedTweetList[1] + \
                #         " " + currentParsedTerm[1]
                # preParsedTweetList = parsedTweetList

                # candidateDependencyNoun.append(parsedTweetList)

                # recursively find the dependency noun on current parsed list
                dependedOnCurrentParsedTerm = self.__findDependencyNoun(
                    parsedTweet, sentStart, start-1, parsedTweet[start], tweets, tweetID)
                currentParsedList[1] = dependedOnCurrentParsedTerm[1] + \
                    " " + currentParsedList[1]
            elif int(parsedTweet[start][6]) == currentNounID \
                    and parsedTweet[start][3] == "O" \
                    and parsedTweet[start][1].lower() in set(["this", "that", "those", "these"]):
                # find the hashtag in this tweet for pronoun like "this, those", except "the"
                # hashtags = tweets[tweetID].hashtags.split()
                # if hashtags:
                #     noSymbolHashtag = re.sub("([#])", "", hashtags[0])
                    # parsedTweetList = list(parsedTweet[start])
                    # if preParsedTweetList:
                    #     parsedTweetList[-1] = parsedTweetList[1] + \
                    #         " " + preParsedTweetList[-1]
                    # else:
                    #     parsedTweetList[-1] = parsedTweetList[1] + \
                    #         " " + currentParsedTerm[1]
                    # # preParsedTweetList = parsedTweetList

                    # parsedTweetList[1] = noSymbolHashtag
                    # parsedTweetList[6] = currentParsedTerm[6]
                    # # candidateDependencyNoun.append(parsedTweetList)
                    # return parsedTweetList
                dependedOnCurrentParsedTerm = self.__findDependencyNoun(
                    parsedTweet, sentStart, start-1, parsedTweet[start], tweets, tweetID)
                currentParsedList[1] = dependedOnCurrentParsedTerm[1] + \
                    " " + currentParsedList[1]
            # handle hashtags for "his", "her", "its", "their"
            elif int(parsedTweet[start][6]) == currentNounID \
                    and parsedTweet[start][3] in set(["O", "D"]) \
                    and parsedTweet[start][1].lower() in set(["his", "her", "its", "their"]):
                hashtags = tweets[tweetID].hashtags.split()
                if hashtags:
                    noSymbolHashtag = re.sub("([#])", "", hashtags[0])
                    parsedTweetList = list(parsedTweet[start])
                    parsedTweetList[1] = noSymbolHashtag
                    parsedTweet[start] = tuple(parsedTweetList)
                    dependedOnCurrentParsedTerm = self.__findDependencyNoun(
                        parsedTweet, sentStart, start-1, parsedTweet[start], tweets, tweetID)
                    currentParsedList[1] = dependedOnCurrentParsedTerm[1] + \
                        " " + currentParsedList[1]
            # handle pre noun of the wh- subject within 2 scopes
            elif currentNounID - int(parsedTweet[start][0]) <= 2 and \
                    currentParsedList[1] in set(["where", "who", "what", "how", "when", "why"]) and \
                    parsedTweet[start][3] in set(["N", "^", "S", "A", "$", "O", "G"]):
                dependedOnCurrentParsedTerm = self.__findDependencyNoun(
                    parsedTweet, sentStart, start-1, parsedTweet[start], tweets, tweetID)
                currentParsedList[1] = dependedOnCurrentParsedTerm[1] + \
                    " " + currentParsedList[1]
            start -= 1
        # if candidateDependencyNoun:
        #     return candidateDependencyNoun
        # return currentParsedTerm
        return currentParsedList

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

    def getCandidateClaims(self, tweets, mergedNoun, sortedSubject2Number, subject2tweetInfo, parsedTweets, initQuery):
        """Get candidate claims from tweets based on subject.

        Arguments:
            tweets {list} -- the list of tweets
            mergedNoun {dict} -- {tweet_id: [noun1, noun2, ...], ...}
            sortedSubject2Number {list} -- [[subject1, number], ...]
            subject2tweetInfo {dict} -- {subject1: (tweet id(str), subjectId(str)), subject2: (tweet id(str), subjectId(str)), ...}
            parsedTweets {dict} -- {tweet_id: [(info_term1), (info_term2), ...], ...}
            initQuery {str} -- the initial query
        Returns:
            list -- [[tweetID, subjectID, afterSubjectIdx, lastObjectID, claim1], ...]
        """
        # make sure subject related to initial query existed.
        candidateClaims = []
        candidateSubjects = [subject for subject,
                             number in sortedSubject2Number]
        for subject in candidateSubjects:
            # print("subject is {}".format(subject))
            for tweetID, subjectId in subject2tweetInfo[subject]:
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
                flag = ["V"]
                objects = self.__getObject(
                    startIndex, totalLen, parsedTweet, rootID,
                    tweetID, startSent, tweets, flag)
                # claimInfo: tweet id, claim

                # if objects or (objects == [] and verb not in set(["is", "was", "are", "were", "be"])):
                if objects and objects[-1][3] in set(["N", "^", "S", "A"]):
                    # print("sub ", type(sub))
                    # print("verb ", type(verb))
                    # print("objects ", type(objects), objects)
                    objects_form = [obj[1] for obj in objects]
                    claim = " ".join([sub[1], verb[1]]+objects_form)
                    afterSubjectIdx = claim.index(sub[1]) + len(sub[1])
                    lastObjectID = int(objects[-1][0])
                    claimInfo = [tweetID, subjectId,
                                 afterSubjectIdx, lastObjectID, claim]
                    candidateClaims.append(claimInfo)
        self.helper.dumpJson(self.fileFolderPath,
                             "candidateClaims.json", candidateClaims)
        print("candidateClaims.json has been saved.")
        # merge the clause with its original claim
        candidateClaimsMergedClause = self.__mergeClause(candidateClaims)
        return candidateClaimsMergedClause

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
        prog = re.compile('[^a-zA-Z]')
        while subjects:
            temp = subjects.pop(0)
            for s in subjects:
                if fuzz.partial_ratio("".join(prog.split(temp.lower())), "".join(prog.split(s.lower()))) >= 90:
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
            tuple -- (root index, subject parsed term, verb parsed term)
        """
        nouns = mergedNoun[tweetID]
        for noun in nouns:
            if int(noun[0]) == int(subjectId):
                break
        # if noun[-1] != "_":
        #     subject = noun[-1]
        # else:
        subject = noun
        rootID = int(noun[6])
        rootIndex = rootID - 1
        verb = parsedTweet[rootIndex]
        return rootIndex, subject, verb

    def __getObject(self, startIndex, totalLen, parsedTweet, rootID, tweetID, startSent, tweets, flag):
        """Get Object from start index.

        Arguments:
            startIndex {int} -- the start index
            totalLen {int} -- the total length of the tweet
            parsedTweet {list} -- [(term_info1), (term_info2), ...]
            rootID {int} -- root ID
            tweetID {int} -- tweet ID
            startSent {int} -- the start index of the current sentence
            tweets {list} -- the list of tweets
            flag {dict} -- the flag for previous pos tag

        Returns:
            list -- the list of parsed terms as objects
        """
        objects = []
        # handle the conjunction with head 0
        if startIndex < totalLen:
            parsedTerm = parsedTweet[startIndex]
            if int(parsedTerm[6]) == 0 and parsedTerm[3] == "&":
                objects.append(parsedTerm)
                afterConjunctionObjects = self.__getObject(
                    startIndex+1, totalLen, parsedTweet,
                    int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                objects = list(objects + afterConjunctionObjects)
        while startIndex < totalLen:
            parsedTerm = parsedTweet[startIndex]
            if parsedTerm[3] == "," and parsedTerm[1] in self.termination:
                break
            # the new parsed term should depend on previous term ID
            if int(parsedTerm[6]) == rootID:
                # handle root_verb verb
                if parsedTerm[3] == "V":
                    tmp = flag.pop()
                    flag.append("V")
                    dependedOnCurrentParsedTerm = self.__findDependencyNoun(
                        parsedTweet, startSent, startIndex-1, parsedTerm,
                        tweets, tweetID)
                    objects.append(dependedOnCurrentParsedTerm)
                    # objects.append(parsedTerm[1])
                    afterVerbObjects = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + afterVerbObjects)
                    # break
                # handle root_verb to do
                elif parsedTerm[3] == "P":
                    tmp = flag.pop()
                    flag.append("P")
                    objects.append(parsedTerm)
                    afterPostposition = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + afterPostposition)
                    # break
                # handle pronoun
                elif parsedTerm[3] == "O" and "V" not in flag:
                    tmp = flag.pop()
                    flag.append("O")
                    objects.append(parsedTerm)
                    afterPostposition = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + afterPostposition)
                # handle root_verb sth.
                elif parsedTerm[3] in set(["N", "^", "S"]):
                    tmp = flag.pop()
                    flag.append("N")
                    # find previously
                    dependencyNounInfos = self.__findDependencyNoun(
                        parsedTweet, startSent, startIndex-1, parsedTerm,
                        tweets, tweetID)
                    # if type(dependencyNounInfos) is list:
                    #     # while dependencyNounInfos:
                    #     #     # add dependency noun
                    #     #     objects.append(
                    #     #         dependencyNounInfos.pop()[1])
                    #     tmp = dependencyNounInfos[-1]
                    #     if tmp[-1] != "_":
                    #         objects.append(tmp[-1])
                    #     else:
                    #         objects.append(tmp[1])
                    # else:
                    #     objects.append(parsedTerm[1])
                    objects.append(dependencyNounInfos)
                    # find postposition
                    postposition = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + postposition)
                    # break
                # handle adj.
                elif parsedTerm[3] == "A" and "N" not in flag and "V" not in flag:
                    tmp = flag.pop()
                    flag.append("A")
                    objects.append(parsedTerm)
                    afterAdj = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + afterAdj)
                    # break
                # handle adv.
                elif parsedTerm[3] == "R" and "V" not in flag:
                    tmp = flag.pop()
                    flag.append("R")
                    objects.append(parsedTerm)
                    afterAdj = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(objects + afterAdj)
                # handle coordinating conjunction
                elif parsedTerm[3] == "&":
                    tmp = flag.pop()
                    flag.append("&")
                    preConjunctionObjects = self.__getObject(
                        0, int(parsedTerm[0])-1, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    afterConjunctionObjects = self.__getObject(
                        startIndex+1, totalLen, parsedTweet,
                        int(parsedTerm[0]), tweetID, startSent, tweets, flag)
                    flag.pop()
                    flag.append(tmp)
                    objects = list(preConjunctionObjects +
                                   [parsedTerm] + afterConjunctionObjects)
                    # break
            startIndex += 1
        return objects[:]

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
            if parsedTweet[startIndex][3] in set(["S", "N", "^", "A"]) and \
                    int(parsedTweet[startIndex][6]) == int(currentParsedTerm[0]):
                return parsedTweet[startIndex]
            startIndex += 1
        return None

    # def __findDependencyonSubject(self, startSent, subjectId, parsedTweet):
    #     """Find the index of the leftmost term dependent on subject.

    #     Arguments:
    #         startSent {int} -- the beginning index of the current sentence
    #         subjectId {int} -- the id of the subject
    #         parsedTweet {list} -- [(info_term1), (info_term2), ...]

    #     Returns:
    #         int -- the index of the leftmost term dependent on subject
    #     """
    #     start = startSent
    #     # Id is bigger than index by one
    #     while start < (subjectId-1):
    #         head = int(parsedTweet[start][6])
    #         if head == subjectId:
    #             return start
    #         start += 1
    #     return subjectId-1

    def __mergeClause(self, candidateClaims):
        """Merge the clause with its original claim.

        Arguments:
            candidateClaims {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]

        Returns:
            list -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
        """
        tweetID2Claims = defaultdict(list)

        for tweetID, subjectID, afterSubjectIdx, lastObjectID, claim in candidateClaims:
            tweetID2Claims[tweetID].append(
                [subjectID, afterSubjectIdx, lastObjectID, claim])
        for tweetID, info in tweetID2Claims.items():
            # handle middle clause
            middleClauseFlag = True
            # handle end clause
            endClauseFlag = True
            if len(info) > 1:
                for i in range(len(info)):
                    pre = info[i]
                    for j in range(len(info)):
                        if i == j:
                            continue
                        curr = info[j]
                        if abs(pre[0] - curr[0]) <= 2:
                            middleClauseFlag = False
                            break
                        elif pre[0] - curr[2] <= 2 or curr[0] - pre[2] <= 2:

                            endClauseFlag = False
                            break
                    if not middleClauseFlag:
                        break
                    if not endClauseFlag:
                        break
                if not middleClauseFlag:
                    if pre[0] < curr[0]:
                        pre[3] = pre[3][:pre[1]+1] + \
                            curr[3] + " " + pre[3][pre[1]+1:]
                        info.pop(j)
                    else:
                        curr[3] = curr[3][:curr[1]+1] + \
                            pre[3] + " " + curr[3][curr[1]+1:]
                        info.pop(i)
                    # tweetID2Claims[tweetID] = info
                if not endClauseFlag:
                    if pre[0] - curr[2] <= 2:
                        curr[3] = curr[3] + " " + pre[3]
                        info.pop(i)
                    elif curr[0] - pre[2] <= 2:
                        pre[3] = pre[3] + " " + curr[3]
                        info.pop(j)
        candidateClaimsMergedClause = [
            [key]+v for key, value in tweetID2Claims.items() for v in value]

        self.helper.dumpJson(self.fileFolderPath,
                             "candidateClaimsMergedClause.json",
                             candidateClaimsMergedClause)
        print("candidateClaimsMergedClause.json has been saved.")
        return candidateClaimsMergedClause

    def rankClaims(self, initQuery, tweets, candidateClaimsMergedClause):
        """Rank candidate claims.

        Arguments:
            initQuery {str} -- the initial query
            tweets {list} -- the list of tweets
            candidateClaimsMergedClause {list} -- [[tweetID, subjectID, afterSubjectIdx, claim1], ...]
            top {int} -- the number of top claims

        Returns:
            list -- [[TweetID, claim1], ...]
        """
        # subjects = list(candidateClaims.keys())
        # relatedSubjects = process.extract(initQuery, subjects)
        # finalSubjects = [sub for sub, score in relatedSubjects if score > 90]
        # if len(finalSubjects) < top:
        #     remain = top - len(finalSubjects)
        #     count = 0
        #     for subject in subjects:
        #         if count >= remain:
        #             break
        #         if subject in finalSubjects:
        #             continue
        #         finalSubjects.append(subject)
        #         count += 1
        # print("final subjects are {}".format(finalSubjects))
        rankedClaims = []
        # for subject in finalSubjects:
        # print("subject is {}".format(subject))
        claimIndex2feature = defaultdict(int)
        # candidateClaims4Subject = candidateClaims[subject]
        for claimIndex, claimInfo in enumerate(candidateClaimsMergedClause):
            tweetIndex = int(claimInfo[0])
            tweet = tweets[tweetIndex]
            # print("claim is {}".format(claimInfo[1]))
            # print("tweet is {}".format(tweet.text))
            # print("tweet's permalink is {}".format(tweet.permalink))
            feature = tweet.reply + tweet.retweets + tweet.favorites
            claimIndex2feature[claimIndex] = feature
        sortedClaimIndex2feature = self.preprocessData.sortDict(
            claimIndex2feature)
        for claimIndex, _ in sortedClaimIndex2feature:
            rankedClaims.append(candidateClaimsMergedClause[claimIndex])

        self.helper.dumpJson(self.fileFolderPath,
                             "claimIndex2feature.json", claimIndex2feature)
        print("claimIndex2feature.json has been saved.")
        self.helper.dumpJson(self.fileFolderPath,
                             "rankedClaims.json", rankedClaims)
        print("rankedClaims.json has been saved.")
        return rankedClaims
