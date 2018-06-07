import click
import codecs
from gensim.models.word2vec import LineSentence
from gensim.models.word2vec import Word2Vec
import os
import sys
sys.path.append('..')
sys.path.append('../GetOldTweets-python')
import got
# from Utility.Helper import Helper
# from Utility.PreprocessData import PreprocessData
import Utility


@click.command()
@click.option('--rootpath', prompt='the root path of data',
              help='the root path of data')
@click.option('--folderpath',
              prompt='the folder paths of data(seperate with whitespace)',
              help='the folder path of data(seperate with whitespace)')
def main_word2vec(rootpath, folderpath):
    """Get main function for getWord2vec."""
    helper = Utility.Helper(rootpath)
    preprocessData = Utility.PreprocessData(rootpath)
    # folderPath = '/local/data/haoxu/Rudetect/Texas Shooting/4'
    # folderPath = os.path.join(rootpath, folderpath)
    # rawDataPath = 'Texas Shooting/4'
    # preprocess the data
    folderpaths = folderpath.split()
    for fpath in folderpaths:
        folderPath = os.path.join(rootpath, fpath, 'final')
        tweets = helper.getTweet(os.path.join(fpath, 'final'))
        with codecs.open(os.path.join(folderPath, "tweets_line_word2vec.txt"),
                         "w", encoding='utf8') as fp:
            for tweet in tweets:
                # print (type(tweet.text.encode('utf8')))
                c1 = preprocessData.cleanTweet(tweet.text)
                c2 = preprocessData.cleanTweet4Word2Vec(c1)
                fp.write(c2.lower() + '\n')

        data4word2vec = LineSentence(os.path.join(folderPath,
                                     "tweets_line_word2vec.txt"))
        if not os.path.exists(os.path.join(rootpath, 'w2vmodel')):
            print ("Start training word2vec model with {}...".format(fpath))
            model = Word2Vec(sentences=data4word2vec, size=100, alpha=0.025,
                             window=5, min_count=5, sample=0, seed=1,
                             workers=1, min_alpha=0.0001, sg=1, hs=1,
                             negative=5, cbow_mean=0
                             )
        else:
            print ("Start updating word2vec model with {}...".format(fpath))
            model = Word2Vec.load(os.path.join(rootpath, 'w2vmodel'))
            model.build_vocab(data4word2vec, update=True)
            model.train(data4word2vec, total_examples=model.corpus_count,
                        epochs=model.iter)
        model.save(os.path.join(rootpath, "w2vmodel"))
    print ("Finished training word2vec and saved it as w2vmodel.")

if __name__ == '__main__':
    main_word2vec()
