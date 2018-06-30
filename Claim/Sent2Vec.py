import sent2vec


class Sent2Vec(object):
    """Sent2Vec model."""

    def __init__(self, modelPath):
        """Initialize the Sent2Vec model.

        Arguments:
            modelPath {str} -- the path to model
        """
        self.encoder = sent2vec.Sent2vecModel()
        self.encoder.load_model(modelPath)

    def encodeSen(self, sentences):
        """Encode sentences.

        Arguments:
            sentences {list} -- a list of sentences

        Returns:
            list -- a list of sentences
        """
        encodedSentences = self.encoder.embed_sentences(sentences)
        return encodedSentences
