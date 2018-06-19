import os
import numpy as np
import scipy.spatial.distance as sd
from skip_thoughts import configuration
from skip_thoughts import encoder_manager


class GetSen2Vec(object):
    """Get sen2vec based on skip thoughts model."""

    def __init__(self, modelPath, checkpointPath):
        """Initialize the GetSen2Vec model.

        Arguments:
            modelPath {str} -- the path to model folder
            checkpointPath {str} -- the filename of mode.ckpt-xxxx
        """
        self.modelPath = modelPath
        self.checkpointPath = os.path.join(modelPath, checkpointPath)
        self.vocabFile = os.path.join(modelPath, "vocab.txt")
        self.embeddingMatrixFile = os.path.join(modelPath, "embeddings.npy")

    def encodeSen(self, sentences):
        """Encode the sentences based on the sent2vec model.

        Arguments:
            sentences {list} -- a list of sentences

        Returns:
            list -- a list of encoded sentences
        """
        encoder = encoder_manager.EncoderManager()
        encoder.load_model(configuration.model_config(),
                           vocabulary_file=self.vocabFile,
                           embedding_matrix_file=self.embeddingMatrixFile,
                           checkpoint_path=self.checkpointPath)
        encodedSentences = encoder.encode(sentences)

        return encodedSentences

    def getSimilarTweets2Claim(self, sentences, claim, encodedClaim, encodedSentences, num=10):
        """Get similar tweets to claim.

        Arguments:
            sentences {list} -- a list of sentences
            claim {str} -- the claim
            encodedClaim {np.array} -- the sen2vec vector of a claim
            encodedSentences {list} -- the total number of encoded sentences

        Keyword Arguments:
            num {int} -- the number of top N (default: {10})

        Returns:
            list -- the list of top N nearest neighbors
        """
        similarSens = []
        scores = sd.cdist(encodedClaim, encodedSentences, "cosine")[0]
        sorted_ids = np.argsort(scores)
        print("Sentence:")
        print("", claim)
        print("\nNearest neighbors:")
        if num + 1 > len(sorted_ids):
            num = len(sorted_ids) - 1
        for i in range(1, num + 1):
            print(" %d. %s (%.3f)" %
                  (i, sentences[sorted_ids[i]], scores[sorted_ids[i]]))
            similarSens.append(sentences[sorted_ids[i]])
        return similarSens
