from nltk import DefaultTagger, UnigramTagger, BigramTagger, TrigramTagger


class SubjectTrigramTagger(object):
    """Create an instance of TrigramTagger.

    With a backoff tagger of a bigram tagger a unigram tagger and a
    default tagger that sets all words to nouns (NN)
    """

    def __init__(self, train_sents):
        """Show parameters.

        train_sents: trained sentences which have already been tagged.
        using Brown, conll2000, and TreeBank corpus.
        """
        t0 = DefaultTagger('NN')
        t1 = UnigramTagger(train_sents, backoff=t0)
        t2 = BigramTagger(train_sents, backoff=t1)
        self.tagger = TrigramTagger(train_sents, backoff=t2)

    def tag(self, tokens):
        """Tag the tokens."""
        return self.tagger.tag(tokens)
