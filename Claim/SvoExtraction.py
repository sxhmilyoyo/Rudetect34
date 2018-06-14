from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import os
import pickle
from .trigram_tagger import SubjectTrigramTagger


class SvoExtraction(object):
    """Extract the SVOs.

    Using the NLTK to get the SVO sentences.
    """

    def __init__(self):
        """Initialize parameters."""
        self.stop = stopwords.words('english')
        self.NOUNS = ['NN', 'NNS', 'NNP', 'NNPS']
        self.VERBS = ['VB', 'VBG', 'VBN', 'VBN', 'VBP', 'VBZ']

    def tokenize_sentences(self, document):
        """Tokenize the sentences into terms.

        document: each tweet on each line
        Return: list
            format: [(tokenizedSents, idx), ...]
        """
        sentences = document.split('\n')
        sentences = [nltk.sent_tokenize(s) for s in sentences]
        tmp = []
        for idx, ss in enumerate(sentences):
            for s in ss:
                tmp.append((s, idx))
        # merge sentences into one list
        # sentences = reduce(lambda a, b: a + b, sentences)
        sentences = [(nltk.word_tokenize(sent), idx) for sent, idx in tmp]
        return sentences

    def get_entities(self, document):
        """Return Named Entites using NLTK Chunking."""
        entities = []
        sentences = self.tokenize_sentences(document)

        # Part of Speech Tagging
        sentences = [nltk.pos_tag(sent) for sent, idx in sentences]
        for tagged_sentence in sentences:
            for chunk in nltk.ne_chunk(tagged_sentence):
                if type(chunk) == nltk.tree.Tree:
                    entities.append(' '.join([c[0] for c in chunk]).lower())
        return entities

    def word_freq_dist(self, document):
        """Return a word count frequency distribution."""
        words = nltk.tokenize.word_tokenize(document)
        words = [word.lower() for word in words if word not in self.stop]
        fdist = nltk.FreqDist(words)
        return fdist

    def get_topic_words(self, document, topic_words, fullPath):
        """Get the topic words which pos tag is related NN."""
        tagSentences = self.tag_sentences(fullPath, None, document)
        # print tagSentences
        tw = set()
        for topic_word in topic_words:
            for tagSentence, idx in tagSentences:
                for tagToken in tagSentence:
                    if(topic_word.lower() == tagToken[0].lower() and
                       tagToken[1] in self.NOUNS):
                        tw.add(topic_word)
        return tw

    def extract_subject(self, document, topic_words, fullPath):
        """Get top10 most frequent Nouns."""
        if not topic_words:
            fdist = self.word_freq_dist(document)
            most_freq_nouns = [w for w, c in fdist.most_common(10)
                               if nltk.pos_tag([w])[0][1] in self.NOUNS]
            topic_nouns = most_freq_nouns[:]
        else:
            topic_nouns = self.get_topic_words(document, topic_words, fullPath)
        # get top 10 entities
        entities = self.get_entities(document)
        top_10_entities = [w for w, c in
                           nltk.FreqDist(entities).most_common(10)]
        # print(top_10_entities)
        # Get the subject noun by the interection of top 10 entities and most
        # frequent nouns
        subject_nouns = [entity for entity in top_10_entities
                         for e in entity.split() if e in topic_nouns]
        print ("subjects are: {}".format(subject_nouns))
        return list(set(subject_nouns))

    def trained_tagger(self, fullPath, existing=False):
        """Return a trained trigram tagger.

        existing: set to True if already trained tagger has been pickled.
        """
        if existing:
            print("trained_tagger.pkl is existed.")
            trigram_tagger = pickle.load(open(os.path.join(fullPath,
                                                           'trained_tagger.pkl'),
                                              'rb'))
            return trigram_tagger
        print ("Training trigram tagger...")
        # Aggregate trained sentences for N-Gram Taggers
        train_sents = nltk.corpus.brown.tagged_sents()
        train_sents += nltk.corpus.conll2000.tagged_sents()
        train_sents += nltk.corpus.treebank.tagged_sents()

        # Create instance of SubjectTrigramTagger and persist instance of it
        trigram_tagger = SubjectTrigramTagger(train_sents)
        pickle.dump(trigram_tagger, open(os.path.join(fullPath,
                                                      'trained_tagger.pkl'),
                                         'wb'))
        print ("Finished training and saving it to {} trained_tagger.pkl.".format(fullPath))
        return trigram_tagger

    def tag_sentences(self, fullPath, subject, document):
        """Return tagged sentences using POS tagging.

        Return: list
            format: [(taggedSents, idx), ...]
                    idx is the id of the original sentence
        """
        if not os.path.exists(os.path.join(fullPath, "trained_tagger.pkl")):
            existed = False
        else:
            existed = True
        trigram_tagger = self.trained_tagger(fullPath=fullPath,
                                             existing=existed)

        # Tokenize Sentences and words
        sentences = self.tokenize_sentences(document)
        if subject:
            self.merge_multi_word_subject(sentences, subject)

        # Filter out sentences where subject is not present
        if subject:
            sentences = [(sentence, idx) for sentence, idx in sentences if subject in
                         [word.lower() for word in sentence]]

        # Tag each sentences
        tagged_sents = [(trigram_tagger.tag(sent), idx) for sent, idx in sentences]
        return tagged_sents

    def merge_multi_word_subject(self, sentences, subject):
        """Merge multi word subjects into one single token.

        ex. [('steve', 'NN'), ('jobs', 'NN')] -> [('steve jobs'), 'NN']
        """
        if len(subject.split()) == 1:
            return sentences
        subject_lst = subject.split()
        sentences_lower = [([word.lower() for word in sentence], idx)
                           for sentence, idx in sentences]
        for i, sent in enumerate(sentences_lower):
            if subject_lst[0] in sent[0]:
                for j, token in enumerate(sent[0]):
                    start = subject_lst[0] == token
                    exists = subject_lst == sent[0][j: j + len(subject_lst)]
                    if start and exists:
                        del sentences[i][0][j + 1: j + len(subject_lst)]
                        sentences[i][0][j] = subject
        return sentences

    def get_svo(self, sentence, subject):
        """Return a dictionary contating.

        subject: the subject determined eariler
        action: the action verb of particular related to the subject
        object: the object the action is referring to
        phrase: list of token, tag pairs for that lie within the indexes of
                the variables above
        """
        # print(sentence)
        subject_idx = next((i for i, v in enumerate(sentence)
                            if v[0].lower() == subject), None)
        endindex = None
        for i, v in enumerate(sentence):
            if v[1] == ".":
                endindex = i

        data = {'subject': subject}
        for i in range(subject_idx, len(sentence)):
            found_action = False
            for j, (token, tag) in enumerate(sentence[i + 1:]):
                if tag in self.VERBS:
                    found_action = True
                if tag in self.NOUNS and found_action:
                    data['object'] = token
                    # data['phrase'] = sentence[i: i + j + 2]
                    data['phrase'] = sentence[i:]
                    if endindex:
                        data['plainPhrase'] = ' '.join([term[0] for term in
                                                        sentence[i:endindex+1]])
                    else:
                        data['plainPhrase'] = ' '.join([term[0] for term in
                                                        sentence[i:]])
                    return data
        return {}
