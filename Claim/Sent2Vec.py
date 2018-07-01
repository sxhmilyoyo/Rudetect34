import sent2vec


class Sent2Vec(object):
    """Sent2Vec model."""

    def __init__(self, modelPath):
        """Initialize the Sent2Vec model.

        Arguments:
            modelPath {str} -- the path to model
        """
        self.encoder = sent2vec.Sent2vecModel()
        print("loading {} model...".format(modelPath))
        self.encoder.load_model(modelPath)
        print("finished loading model.")

    def encodeSen(self, sentences):
        """Encode sentences.

        Arguments:
            sentences {list} -- a list of sentences

        Returns:
            list -- a list of sentences
        """
        encodedSentences = self.encoder.embed_sentences(sentences)
        return encodedSentences
