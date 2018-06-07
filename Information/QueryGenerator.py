import sys
sys.path.append("..")
from collections import Counter
from collections import defaultdict
from nltk.stem.wordnet import WordNetLemmatizer
import os
import Utility


class QueryGenerator(object):
    """Generate the query."""

    def __init__(self, rootpath):
        """Initialize the parameters.

        Parameters
        ----------
        rootpath : str
            the root path of data
        folderpath : str
            the folder path of the event

        Returns
        -------
        None

        """
        self.rootpath = rootpath
        self.DO = ['VBG', 'VBN', 'VB', 'VBD', 'VBP', 'VBZ']
        self.BE = ['BE', 'BEG', 'BEM', 'BER', 'BEZ', 'BEN', 'BED ', 'BEDZ']
        self.MD = ['MD']
        self.punctuation = [".", "?", "/", "...", ",", "!", ":", ";"]
        self.VERBs = self.DO + self.BE + self.MD
        self.helper = Utility.Helper(rootpath)

    def getAuxiliary(self, subject_tag, verb_tag):
        """Get the auxiliary for the verb.

        Parameters
        ----------
        subject : str
            the pos tag of the subject
        verb : str
            the pos tag of the verv

        Returns
        -------
        str
            the auxiliary for the different pos tag of verb

        """
        if verb_tag in self.DO:
            if 'VBG' == verb_tag:
                if 'S' in subject_tag:
                    return 'are'
                else:
                    return 'is'
            if 'VBN' == verb_tag:
                if 'S' in subject_tag:
                    return 'have'
                else:
                    return 'has'
            return {
                'VB': 'do',
                'VBD': 'did',
                'VBP': 'do',
                'VBZ': 'does'
            }.get(verb_tag, '')
        else:
            return None

    def generateQuery(self, folderpath):
        """Generate the queries for all svos.

        Save {subject: [query1, query2, ...]} to subject2queries.json file
        Returns
        -------
        None

        """
        folderPath = os.path.join(folderpath, 'final')
        subject2svos = self.helper.loadJson(os.path.join(folderPath,
                                                         'subject2svos.json'))
        subject2queries = defaultdict(list)
        for subject in subject2svos:
            svos = subject2svos[subject]
            for svo in svos:
                if not svo:
                    continue
                # s = svo['subject']
                # o = svo['object']
                taggedSents = svo['phrase']
                phrase = []
                v = None
                for taggedToken in taggedSents:
                    if taggedToken[1] in self.VERBs and not v:
                        v = taggedToken
                        subject_tag = taggedSents[0][1]
                        auxiliary = self.getAuxiliary(subject_tag, v[1])
                        if auxiliary:
                            if v[1] not in ['VBG', 'VBN']:
                                v[0] = WordNetLemmatizer().lemmatize(
                                    v[0].lower(), 'v')
                            phrase.insert(0, auxiliary)
                            phrase.append(v[0])
                        else:
                            phrase.insert(0, v[0])
                    else:
                        phrase.append(taggedToken[0])
                if phrase[-1] in self.punctuation:
                    del phrase[-1]
                query = ' '.join(phrase) + "?"
                subject2queries[subject].append({'svo': svo['plainPhrase'],
                                                'query': query})
            # # get top10 queries
            # cnt = Counter(subject2queries[subject])
            # print(cnt)
            # top10queries = [q[0] for q in cnt.most_common(3)]
            # subject2queries[subject] = top10queries
        print("The subject2svoquery.json has been saved.")
        self.helper.dumpJson(
            folderPath, 'subject2svoqueries.json', subject2queries)
