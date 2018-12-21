import sys
# sys.path.append("..")
sys.path.append('/home/hao/Workplace/HaoXu/Library/GetOldTweets-python')
sys.path.append('/home/hao/Workplace/HaoXu/Library/ark-tweet-nlp-python')
sys.path.append(
    '/home/hao/Workplace/HaoXu/Library/models/research/skip_thoughts')
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
@click.option("--eps", "-p", help="the eps for DBSCAN")
def main(rootpath, folderpath, query, start, end, eps=0.5):
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

    # # get tweets
    # print('='*100)
    # print('Getting tweets ...')
    # print('='*100)
    # # workFlow.getTweets(query, start, end)

    # get Claims
    print('='*100)
    print('Getting subject ...')
    print('='*100)
    # local
    workFlow.getClaims(query)
    # farber
    # workFlow.getClusterRankClaims(query, float(eps))

    # # get similar news
    # print("="*100)
    # print('Getting News ...')
    # print("="*100)
    # workFlow.getNews(folderpath)

    # # get corpus for classification of the event
    # print('='*100)
    # print('Getting corpus for classification of the event ...')
    # print('-'*100)
    workFlow.getCorpus4Classification(folderpath)
    # print('='*100)

if __name__ == '__main__':
    main()