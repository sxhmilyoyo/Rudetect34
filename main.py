import sys
# sys.path.append("..")
sys.path.append('/home/hao/Workplace/HaoXu/Library/GetOldTweets-python')
sys.path.append('/home/hao/Workplace/HaoXu/Library/ark-tweet-nlp-python')
sys.path.append('/home/hao/Workplace/HaoXu/Library')
import click
import logging
logging.disable(logging.CRITICAL)
# print sys.path
import Main
import Utility
import os


@click.command()
@click.option("--rootpath", "-r", help="the root path of the data")
@click.option("--folderpath", "-f", help="the folder path of the event")
@click.option("--query", "-q", help="the hashtags you want to search")
@click.option("--start", "-s", help="the start date of the event")
@click.option("--end", "-e", help="the end date of the event")
def main(rootpath, folderpath, query, start, end):
    """Get the main function for the workflow.

    Parameters
    ----------
    rootpath : str
        the root path of the data
    folderpath : str
        the folder path of the event
    query : str
        the hashtags you want to search
        format1: #hashtag1 #hashtag2
        format2: #hashtag1 AND hashtag2
    start : str
        the start date of the event
        format: "yyyy-mm-dd"
    end : str
        the end date of the event
        format: "yyyy-mm-dd"

    Returns
    -------
    None

    """
    # helper = Utility.Helper(rootpath)
    workFlow = Main.WorkFlow(rootpath, folderpath)
    # get tweets

    """print('='*100)
    print('Getting tweets ...')
    print('='*100)
    workFlow.getTweets(query, start, end)"""

    """# get word2vec
    print('='*100)
    print('Getting word2vec ...')
    print('='*100)
    workFlow.getWord2Vec()"""

    # get Nouns
    print('='*100)
    print('Getting subject ...')
    print('='*100)
    workFlow.getSubject(query)
    """# get the topic model
    print('='*100)
    print('Getting topic model ...')
    print('-'*100)
    numTopic = 10
    # preNumTopic = 0
    # while numTopic != preNumTopic:
    dist = workFlow.getTopicPmi(folderpath, numTopic)
    numTopic = helper.getTopicNum(dist)
    print('='*100)
    # get cluster
    print('='*100)
    print('Getting clusters ...')
    print('-'*100)
    workFlow.getCluster("tfidf", numTopic)
    print('='*100)
    # get topic model and SVO for each cluster
    print('='*100)
    print('Running for clusters: getting topic model and SVO and corpus for classification...')
    print('-'*100)
    workFlow.run4cluster()
    print('='*100)
    # get corpus for classification of the event
    print('='*100)
    print('Getting corpus for classification of the event ...')
    print('-'*100)
    workFlow.getCorpus4Classification(folderpath, 'event')
    print('='*100)
    # get similarity between statements of the event
    print('='*100)
    print('Getting similarity between statements ...')
    print('-'*100)
    workFlow.getSimilarity4Statements(folderpath)
    print('='*100)"""
    # events = [d for d in os.listdir(rootpath) if os.path.isdir(rootpath+"/"+d)]
    # topics = []
    # for event in events:
    #     print(event)
    #     tmp = []
    #     for i in event.split('_'):
    #         if not i.isdigit():
    #             tmp.append(i)
    #     topics.append(' '.join(tmp))
    # workFlow.run4events(events, topics)


if __name__ == '__main__':
    main()
