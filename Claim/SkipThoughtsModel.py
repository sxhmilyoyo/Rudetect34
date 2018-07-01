# from skip_thoughts import configuration
# from skip_thoughts import encoder_manager
import os


class SkipThoughtsModel(object):
    """Skip-Thoughts Model."""

    def __init__(self, modelPath, checkpointPath):
        """Initialize skip though model.

        Arguments:
            modelPath {str} -- the path to model
            checkpointPath {str} -- the filename of mode.ckpt-xxxx
        """
        self.modelPath = modelPath
        self.checkpointPath = os.path.join(modelPath, "..", checkpointPath)
        self.vocabFile = os.path.join(modelPath, "vocab.txt")
        self.embeddingMatrixFile = os.path.join(
            modelPath, "embeddings.npy")

        self.encoder = encoder_manager.EncoderManager()
        self.encoder.load_model(configuration.model_config(),
                                vocabulary_file=self.vocabFile,
                                embedding_matrix_file=self.embeddingMatrixFile,
                                checkpoint_path=self.checkpointPath)

    def encodeSen(self, sentences):
        """Encode the sentences based on the sent2vec model.

        Arguments:
            sentences {list} -- a list of sentences

        Returns:
            list -- a list of encoded sentences
        """

        encodedSentences = self.encoder.encode(sentences)

        return encodedSentences
