import os
import numpy as np
import scipy.spatial.distance as sd
from skip_thoughts import configuration
from skip_thoughts import encoder_manager
from nltk import sent_tokenize
from nltk import word_tokenize
from collections import defaultdict
import Utility


class TweetsExtractor4Claim(object):
    """Get similar tweets for claim based on sen2vec in skip thoughts model."""

    def __init__(self, modelPath, checkpointPath):
        """Initialize the TweetsExtractor4Claim model.

        Arguments:
            modelPath {str} -- the path to model folder
            checkpointPath {str} -- the filename of mode.ckpt-xxxx
        """
        self.modelPath = modelPath
        self.checkpointPath = os.path.join(modelPath, checkpointPath)
        self.vocabFile = os.path.join(modelPath, "vocab.txt")
        self.embeddingMatrixFile = os.path.join(modelPath, "embeddings.npy")

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
