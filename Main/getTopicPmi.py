import click
import codecs
import os
import sys
# sys.path.insert(0, 'chowmein')
sys.path.append('..')
sys.path.append('../GetOldTweets-python')
from chowmein import label_topic
from collections import defaultdict
# from Utility.Helper import Helper
# from Utility.PreprocessData import PreprocessData
import Utility


@click.command()
@click.option('--rootpath', '-r', help='the root path of data')
@click.option('--folderpath', '-f', help='the folder path of data')
@click.option('--numTopic', '-n', type=int, help='the number of topic')
def main_topicPmi(rootpath, folderpath, numTopic):
    """Get topic with pmi."""
    # get tweets
    helper = Utility.Helper(rootpath)
    folderPath = os.path.join(folderpath, 'final')
    tweets = helper.getTweet(folderPath)
    # preprocess tweets
    preprocessData = Utility.PreprocessData(rootpath)
    # dataPath = "/local/data/haoxu/Rudetect/DevinKelley_Antifa/"
    with codecs.open(os.path.join(rootpath, folderPath, "tweets_line.txt"),
                     "w", encoding='utf8') as fp:
        for tweet in tweets:
            # print (type(tweet.text.encode('utf8')))
            c1 = preprocessData.cleanTweet(tweet.text)
            # c2 = preprocessData.cleanTweet4Word2Vec(c1)
            fp.write(c1 + '\n')

    # get topic with pmi
    corpus_path = os.path.join(rootpath, folderPath, "tweets_line.txt")
    n_topics = numTopic
    n_top_words = 5
    preprocessing_steps = ['tag']
    n_cand_labels = 100
    label_min_df = 5
    label_tags = ['NN,NN', 'JJ,NN']
    n_labels = 3
    lda_random_state = 12345
    lda_n_iter = 10000

    labels, words = label_topic.get_topic_labels(corpus_path,
                                                 n_topics,
                                                 n_top_words,
                                                 preprocessing_steps,
                                                 n_cand_labels,
                                                 label_min_df,
                                                 label_tags,
                                                 n_labels,
                                                 lda_random_state,
                                                 lda_n_iter)

    print("\nTopical labels:")
    print("-" * 20)
    topics = defaultdict(list)
    for i, labels in enumerate(labels):
        topics[i] = map(lambda l: ' '.join(l), labels)
        print(u"Topic {}: {}".format(i, ', '.join(map(lambda l:
                                                      ' '.join(l), labels))))

    helper.dumpJson(folderPath, "tweets_topic_words_pmi.json", words)
    # with open(dataPath + "tweets_topic_words_pmi_0102.json", "w") as fp:
    #     json.dump(words, fp, indent=4)
    print("tweets_topic_words_pmi.json has been saved.")
    helper.dumpJson(folderPath, "tweets_label_words_pmi.json", labels)
    # with open(dataPath + "tweets_topic_label_pmi_0102.json", "w") as fp:
    #     json.dump(topics, fp, indent=4)
    print("tweets_topic_label_pmi.json has been saved.")

if __name__ == '__main__':
    main_topicPmi()
