from collections import Counter
from collections import defaultdict
import csv
import nltk
import os
import preprocessor as p
import random
import re
# import sys
# sys.path.append('../GetOldTweets-python')
# import got
import SVO
import Utility
import operator


class PreprocessData(object):
    """Preprocess data.

    tokenizer(text)
    rmStopWord(tokens)
    stemmer(tokens)
    getCorpus(folderName)
    cleanTweet(text)
    """

    def __init__(self, rootPath):
        """Initialize the parameters.

        porter: PorterStemmer from nltk
        stopwords: stopwords from NLTK
        """
        self.rootPath = rootPath
        self.porter = nltk.PorterStemmer()
        self.stopwords = nltk.corpus.stopwords.words("english")
        self.helper = Utility.Helper(rootPath)

    def tokenizer(self, text):
        """Use regexp to tokenize."""
        # print text
        return re.findall(r"\w+", text)

    def rmStopWord(self, tokens):
        """Remove stop words."""
        return [w for w in tokens if w.lower() not in self.stopwords]

    def stemmer(self, tokens):
        """Stem token."""
        return [self.porter.stem(token) for token in tokens]

    def getCorpus_old(self, folderPath):
        """Get corpus after tokenizing, removing stopwords and stemming."""
        tweets = self.helper.loadPickle(folderPath+"/tweets.pkl")
        for tweet in tweets:
            self.stemmer(self.rmStopWord(self.tokenizer(tweet.text())))

    def cleanTweet(self, text):
        """Clean tweets.

        remove URL, EMOJI, MENTION, SMILEY, HASHTAGS, ASCII
        """
        # if 'http' in text:
        #     text = text[:text.find('http') - 1]
        p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.MENTION, p.OPT.SMILEY)
        cleaned = p.clean(text)
        noHashtags = ' '.join(re.sub("([#])", " ", cleaned).split())
        return noHashtags

    def getCorpus(self, folderPath):
        """Get list of list of tokens from .pkl file."""
        corpus = []
        tweets = self.helper.getTweet(folderPath)
        for tweet in tweets:
            content = tweet.text
            cleanedContent = self.cleanTweet(content)
            tokens = self.tokenizer(cleanedContent)
            corpus.append(tokens)
        return corpus

    def getTokens(self, content):
        """Get list of list of tokens from .pkl file."""
        regex = re.compile('[^a-zA-Z]')
        cleanedContent = regex.sub(' ', content)
        tokens = self.tokenizer(cleanedContent)
        return tokens

    def getId2Corpus(self, folderPath):
        """Map the index to corpus.

        Save the {id: tweet content} into id2Corpus.json
        """
        corpus = defaultdict(str)
        tweets = self.helper.getTweet(folderPath)
        index = 0
        for tweet in tweets:
            content = unicode(tweet.text, errors='ignore')
            cleanedContent = self.cleanTweet(content)
            corpus[index] = cleanedContent
            index += 1
        self.helper.dumpJson(folderPath, 'id2Corpus.json', corpus)

    def cleanTweet4Word2Vec(self, text):
        """Clean tweets for building word2vec model.

        Based on the cleanTweet() result, remove noncharacters and subsitute
        char(') with char(_)
        """
        noAscii = self.cleanTweet(text)
        onlyCharac = re.sub('[^a-zA-z0-9 \']', ' ', noAscii)
        subPrime = re.sub('\'', '_', onlyCharac)
        return subPrime

    def cleanSnippet4Classification(self, text):
        """Clean snippet for building word2vec model.

        Convert tab to whitespace
        """
        noTab = re.sub(' +', ' ', text)
        noNewline = re.sub('\n', ' ', noTab)
        return noNewline

    def storeTweets4Clusters(self, folderPath):
        """Store tweets object into different clusters.

        Based on the doc2Label.pkl
        """
        d2l = self.helper.loadPickle(os.path.join(folderPath, 'doc2Label.pkl'))
        tweets = self.helper.getTweet(folderPath)
        docIdx = 0
        label2tweet = defaultdict(list)
        for tweet in tweets:
            label2tweet[d2l[docIdx]].append(tweet)
            docIdx += 1
        for l in label2tweet.keys():
            path = os.path.join(folderPath, 'clusterData', str(l), 'final',
                                'rawData')
            if not os.path.exists(path):
                os.makedirs(path)
            self.helper.dumpPickle(path, 'tweets.pkl', label2tweet[l])
            print ("tweets.pkl for cluster {} has been saved.".format(l))

    def getTop5SVO(self, folderPath, svos):
        """Get top5 SVOs.

        Parameters
        ----------
        svos : list
            [svo1, svo2, ...]
        folderPath : str
            the folder path of the data

        Returns
        -------
        list
            [svo1, svo2, ...]

        """
        # svoExtraction = SVO.SvoExtraction()
        svo2info = defaultdict(int)
        # for svo in svos:
        # print(svos)
        for svo, idx in svos:
            if not svo:
                continue
            svoPhrase = svo['plainPhrase']
            # print("svoPhrase: ", svoPhrase)
            tweets = list(self.helper.getTweet(folderPath))
            # print("originalSVO: ", tweets[idx].text)
            if svoPhrase not in svo2info:
                retweet_favorites_num = tweets[idx].retweets + tweets[idx].favorites + 1
                svo2info[svoPhrase] = retweet_favorites_num
            else:
                svo2info[svoPhrase] += 1
            # for tweet in self.helper.getTweet(folderPath):
            #     """
            #     In order to find the tweets that contains the svoPhrase
            #     need to address the tweet content in the same way as the
            #     svoPhrase:
            #     cleanTweet() then tokenization and ' '.join()
            #     """
            #     tweet_c = self.cleanTweet(tweet.text)
            #     tweet_e = ' '.join([' '.join(s) for s in
            #                         svoExtraction.tokenize_sentences(tweet_c)])
            #     if svoPhrase.lower() in tweet_e.lower():
            #         # the weight includes: retweets, like and number
            #         retweet_favorites_num = tweet.retweets + tweet.favorites
            #         + 1
            #         svo2info[svoPhrase] += retweet_favorites_num
            # if svoPhrase not in svo2info.keys():
            #     print("{} NOT FOUND!!! {}".format('*' * 10, '*' * 10))
            #     for tweet in self.helper.getTweet(folderPath):
            #         tweet_c = self.cleanTweet(tweet.text)
            #         tweet_e = ' '.join(
            #             [' '.join(s) for s in
            #              svoExtraction.tokenize_sentences(tweet_c)])
            #         # print(tweet_e.lower())
            #     print("Phrase {}".format(svoPhrase.lower()))
        cnt = Counter(svo2info)
        top5SVOPlainPhrase = [c[0] for c in cnt.most_common(5)]
        # print("="*100)
        # print(top5SVOPlainPhrase)
        # print("="*100)
        res = []
        for svo, idx in svos:
            if svo and svo['plainPhrase'] in top5SVOPlainPhrase:
                top5SVOPlainPhrase.remove(svo['plainPhrase'])
                res.append(svo)
        # print(res)
        return res

    def getCorpus4csv(self, folderPath, target):
        """Get corpus that divided by tab.

        Parameters
        ----------
        folderPath : str
            the folder path

        Returns
        -------
        None
            save the corpus into .csv file

        """
        tweets = self.helper.getTweet(folderPath)
        # p = os.path.join(self.rootPath, folderPath, "corpus.csv")
        title = ['ID', 'Target', 'Tweet', 'Stance', 'Date', 'Origin']
        s = ['NONE', 'AGAINST', 'FAVOR']
        data = []
        for tweet in tweets:
            origin = tweet.text
            c1 = self.cleanTweet4Word2Vec(origin)
            content = c1
            idx = tweet.id
            r = random.randint(0, 2)
            date = tweet.date
            data.append([idx, target, content, s[r], date, origin])

        self.helper.dumpCsv(folderPath, "corpus.csv", title, data)
        # with open(p, "wb") as fp:
        #     filewriter = csv.writer(fp, delimiter='\t')
        #     filewriter.writerow(['ID', 'Target', 'Tweet', 'Stance', 'Date'])
        #     for tweet in tweets:
        #         content = tweet.text
        #         idx = tweet.id
        #         r = random.randint(0, 2)
        #         date = tweet.date
        #         filewriter.writerow([idx, target, content, s[r], date])

    def getCorpus4csvFromStatements(self, folderPath):
        """Get corpus from statements that divided by tab.

        Parameters
        ----------
        folderPath : str
            the folder path

        Returns
        -------
        None
            save the corpus into .csv file

        """
        # tweets = self.helper.getTweet(folderPath)
        # with open(os.path.join(self.rootPath, folderPath, "candidate_statements.txt")) as fp:
            # statements = fp.readlines()
        statements = self.helper.loadCsv(folderPath, "candidate_statements.csv")
        if statements is None or len(statements) == 0:
            return
        # p = os.path.join(self.rootPath, folderPath, "corpus_statements.csv")

        title = ['ID', 'Target', 'Tweet', 'Stance', 'Origin']
        s = ['NONE', 'AGAINST', 'FAVOR']
        data = []
        for i in range(len(statements)):
            if statements[i]:
                origin = statements[i][1].strip("\n")
                c1 = self.cleanTweet4Word2Vec(origin)
                content = c1
                idx = i + 1
                r = random.randint(0, 2)
                target = statements[i][0]
                data.append([idx, target, content, s[r], origin])
        self.helper.dumpCsv(folderPath, "corpus_statements.csv", title, data)

        # with open(p, "wb") as fp:
        #     filewriter = csv.writer(fp, delimiter='\t')
        #     filewriter.writerow(['ID', 'Target', 'Tweet', 'Stance'])
        #     for i in range(len(statements)):
        #         if statements[i]:
        #             content = statements[i].strip('\n')
        #             idx = i + 1
        #             r = random.randint(0, 2)
        #             filewriter.writerow([idx, target, content, s[r]])

    def getCandidateClaims(self, folderPath):
        """Get candidate claims from subject2rankedClaims.json.
        
        Arguments:
            folderPath {str} -- the folder path to event
        
        Returns:
            list -- [claim1, claim2, ...]
        """
        claims = []
        filePath = os.path.join(folderPath, "final", "subject2rankedClaims.json")
        subject2rankedClaims = self.helper.loadJson(filePath)
        for subject in subject2rankedClaims.keys():
            for _, claim in subject2rankedClaims[subject]:
                claims = claim.lower()
        return claims

    def getTweetsFromTweetsLine(self, folderPath):
        """Get whole tweets for each cluster."""
        # folderPath = os.path.join(folderPath, 'final', 'clusterData')
        # foldernames = os.listdir(os.path.join(self.rootPath, folderPath))
        total = []
        # for foldername in foldernames:
        filePath = os.path.join(self.rootPath, folderPath, 'final', "tweets_line.txt")
        with open(filePath) as fp:
            tweets = fp.readlines()
        for tweet in tweets:
            c1 = self.cleanTweet4Word2Vec(tweet)
            total.append(c1.lower())
        return total

    def getCandidateStatements4Cluster(self, folderPath):
        """Get candidate statements from subject2svoqueries.json for each cluster.

        Parameters
        ----------
        folderPath : str
            the event folder path.

        Returns
        -------
        list
            [statement1, statement2, ...].

        """
        total = []
        filePath = os.path.join(folderPath, 'final', "subject2svoqueries.json")
        subject2svoqueries = self.helper.loadJson(filePath)
        # if os.path.exists(os.path.join(self.rootPath, folderPath, 'final', "candidate_statements.txt")):
                    # os.remove(os.path.join(self.rootPath, folderPath, 'final', "candidate_statements.txt"))
        data = []
        queries = []
        for topic in subject2svoqueries.keys():
            print(topic)
            for svoquery in subject2svoqueries[topic]:
                # with open(os.path.join(self.rootPath, folderPath, 'final', "candidate_statements.txt"), "a") as fp:
                    # fp.write(svoquery['svo'] + "\n")
                data.append([topic, svoquery['svo']])
                queries.append([topic, svoquery['query']])
                c1 = self.cleanTweet4Word2Vec(svoquery['svo'])
                total.append(c1.lower())
        self.helper.dumpCsv(os.path.join(folderPath, 'final'), "candidate_queries.csv", ['Subject', 'Query'], queries)        
        self.helper.dumpCsv(os.path.join(folderPath, 'final'), "candidate_statements.csv", ['Subject', 'Statement'], data)        
        return total

    def getCorpus4csvFromSnippets(self, folderpath):
        """Get corpus from snippets that divided by tab.

        Parameters
        ----------
        folderPath : str
            the folder path

        Returns
        -------
        None
            save the corpus into .csv file

        """
        snippets = self.helper.loadJson(folderpath+"/snippets.json")
        if snippets is None or len(snippets) == 0:
            return
        
        title = ['ID', 'Target', 'Tweet', 'Stance', 'Origin', 'Total', 'Origin_ID']
        s = ['NONE', 'AGAINST', 'FAVOR']
        data = []
        
        k = 1
        for i in range(len(snippets)):
            if snippets[i]:
                for j in range(len(snippets[i])): 
                    if snippets[i][j]:
                        origin = snippets[i][j]['snippets']
                        c_origin = self.cleanSnippet4Classification(snippets[i][j]['snippets'])
                        c1 = self.cleanTweet4Word2Vec(origin)
                        c2 = self.cleanSnippet4Classification(c1)
                        content = c2
                        idx = k
                        r = random.randint(0, 2)
                        target = snippets[i][j]['topic']
                        total = len(snippets[i])
                        data.append([idx, target, content, s[r], c_origin, total, snippets[i][j]['id']])
                        k += 1
        self.helper.dumpCsv(folderpath, "corpus_snippets.csv", title, data)
    
    def sortDict(self, d):
        """Sort the dictionary.

        Args:
            d (dict): the dictionary
        Returns:
            list: sorted_dict
        """
        sorted_dict = sorted(d.items(), key=operator.itemgetter(1),
                             reverse=True)
        return sorted_dict

    # def getData4Sen140API(self, folderpath):
    #     """Generate the data for Sentiment140API.
    #
    #     Parameters
    #     ----------
    #     folderpath : str
    #         the folder path of the data
    #
    #     Returns
    #     -------
    #     generator
    #         [
    #             {'text': ..., 'id': ..., 'query': ..., 'topic': ...},
    #             {'text': ..., 'id': ..., 'query': ..., 'topic': ...},
    #             ...
    #         ]
    #
    #     """
    #     folderPath = os.path.join(folderpath, 'final', 'snippets')
    #     subjectFolderPaths = os.listdir(folderPath)
    #     for subjectFolderPath in subjectFolderPaths:
    #         filenames = os.listdir(os.path.join(folderPath, subjectFolderPath))
    #         for filename in filenames:
    #             fullPath = os.path.join(folderPath, subjectFolderPath, filename
    #                                     )
    #             snippets = self.helper.loadJson(fullPath)
    #             data = []
    #             for snippet in snippets:
    #                 data.append({'text': snippet['snippets'],
    #                              'id': int(snippet['id'][-1])})
    #             yield data
