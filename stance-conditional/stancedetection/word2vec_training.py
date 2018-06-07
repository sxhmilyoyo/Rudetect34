import sys
sys.path.append("..")
print(sys.path)
from gensim.models import word2vec, Phrases
import logging
from readwrite import reader, writer
import os
from preprocess import tokenise_tweets, build_dataset, transform_tweet, transform_labels
import numpy as np


def trainPhrasesModel(tweets):
    """
    Train phrases model, experimental, not used
    :param tweets: list of tokenised tweets
    :return:
    """
    print("Learning multiword expressions")
    bigram = Phrases(tweets)
    bigram.save("../out/phrase_all.model")

    print("Sanity checking multiword expressions")
    test = "i like donald trump , go hillary clinton , i like jesus , jesus , legalisation abortion "
    sent = test.split(" ")
    print(bigram[sent])
    return bigram[tweets]


def trainWord2VecModel(tweets, modelname):
    #tweets = trainPhrasesModel(tweets)

    print("Starting word2vec training")
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # set params
    num_features = 100  # 91    # Word vector dimensionality
    min_word_count = 5   # Minimum word count
    num_workers = 4       # Number of threads to run in parallel
    context = 5          # Context window size
    downsampling = 1e-3   # Downsample setting for frequent words
    trainalgo = 1  # cbow: 0 / skip-gram: 1

    print("Training model...")

    if os.path.exists(modelname):
        model = word2vec.Word2Vec.load(modelname)
        model.build_vocab(tweets, update=True)
        model.train(tweets, total_examples=model.corpus_count, epochs=model.iter)
    else:
        model = word2vec.Word2Vec(tweets, workers=num_workers, size=num_features,
                                  min_count=min_word_count, window=context, sample=downsampling, sg=trainalgo)

        # add for memory efficiency
        model.init_sims(replace=True)

    # save the model
    model.save(modelname)


# find most similar n words to given word
def applyWord2VecMostSimilar(modelname="../data/skip_nostop_single_100features_10minwords_5context", word="#gabapentin",
                             top=10):
    model = word2vec.Word2Vec.load(modelname)
    print("Find ", top, " terms most similar to ", word, "...")
    for res in model.most_similar(word, topn=top):
        print(res)
    print("Finding terms containing ", word, "...")
    for v in model.wv.vocab:
        if word in v:
            print(v)


if __name__ == '__main__':
    # unk_tokens = [["unk"], ["unk"], ["unk"], ["unk"], [
    #     "unk"], ["unk"], ["unk"], ["unk"], ["unk"], ["unk"]]
    # tweets, targets, labels, ids = reader.readTweetsOfficial(
    #     "../data/semeval2016-task6-train+dev.txt")
    # tweet_tokens = tokenise_tweets(tweets, stopwords="most")
    # tweets_trump, targets_trump, labels_trump, ids_trump = reader.readTweetsOfficial(
    #     "../data/downloaded_Donald_Trump.txt", "utf-8", 1)
    # tweet_tokens_trump = tokenise_tweets(tweets_trump, stopwords="most")
    #
    # tweets_Gampa, targets_Gampa, labels_Gampa, ids_Gampa = reader.readTweetsOfficial(
    #     "/local/data/haoxu/Rudetect/Gabapentin_0628_0121/final/corpus.csv", "utf-8", 1)
    # tweets_tokens_Gampa = tokenise_tweets(tweets_Gampa, stopwords="most")
    #
    # tweets_unlabelled = reader.readTweets(
    #     "../data/additionalTweetsStanceDetection.json")
    # tweet_tokens_unlabelled = tokenise_tweets(
    #     tweets_unlabelled, stopwords="most")
    #
    # trainWord2VecModel(unk_tokens + tweet_tokens + tweet_tokens_trump + tweet_tokens_unlabelled +
    #                    tweets_tokens_Gampa, "../out/skip_nostop_single_100features_5minwords_5context_big")
    modelname = "/local/data/haoxu/Rudetect_additional/stance-conditional/out/skip_nostop_single_100features_5minwords_5context_big"
    folderPath = "/local/data/haoxu/Rudetect"
    dirnames = [d for d in os.listdir(
        folderPath) if os.path.isdir(folderPath + '/' + d)]
    final_tweets_tokens = []
    for dirname in dirnames:
        print(dirname)
        p = os.path.join(folderPath, dirname, 'final', 'corpus.csv')
        tweets, target, labels, ids = reader.readTweetsOfficial(p, "utf-8")
        tweets_tokens = tokenise_tweets(tweets, stopwords="most")
        final_tweets_tokens += tweets_tokens
    trainWord2VecModel(final_tweets_tokens, modelname)
    # applyWord2VecMostSimilar(
    #     "../out/skip_nostop_single_100features_5minwords_5context_big")
