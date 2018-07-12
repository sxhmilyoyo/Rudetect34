import sys
# sys.path.append("..")
sys.path.append('/home/1877/Library/GetOldTweets-python')
sys.path.append('/home/1877/Library/ark-tweet-nlp-python')
# sys.path.append(
#     '/home/1877/Library/models/research/skip_thoughts')
# sys.path.append('/home/hao/Workplace/HaoXu/Library')
# import click
import logging
logging.disable(logging.CRITICAL)
# print sys.path
import Main
import Utility
import os


# @click.command()
# @click.option("--rootpath", "-r", help="the root path of the data")
# @click.option("--folderpath", "-f", help="the folder path of the event")
# @click.option("--query", "-q", help="the hashtags you want to search")
# @click.option("--start", "-s", help="the start date of the event")
# @click.option("--end", "-e", help="the end date of the event")
def main(rootpath, folderpath, query, start, end, eps):
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
    # workFlow.getTweetsFromPheme()
    # # workFlow.getTweets(query, start, end)

    # # get word2vec
    # print('='*100)
    # print('Getting word2vec ...')
    # print('='*100)
    # workFlow.getWord2Vec()

    # # get Claims
    # print('='*100)
    # print('Getting subject ...')
    # print('='*100)
    # # farber
    # workFlow.getClusterRankClaims(query, float(eps))
    # # # workFlow.getClaims(query)

    # get similar news
    print("="*100)
    print('Getting News ...')
    print("="*100)
    # workFlow.getNews(folderpath)
    workFlow.getSnippets(folderpath)

    """# get the topic model
    print('='*100)
    print('Getting topic model ...')
    print('-'*100)
    numTopic = 10
    # preNumTopic = 0
    # while numTopic != preNumTopic:
    dist = workFlow.getTopicPmi(folderpath, numTopic)
    numTopic = helper.getTopicNum(dist)
    """

    """# # get cluster
    # print('='*100)
    # print('Getting clusters ...')
    # print('-'*100)
    # workFlow.getSimilarTweets4Claim()"""

    """
    # get topic model and SVO for each cluster
    print('='*100)
    print('Running for clusters: getting topic model and SVO and corpus for classification...')
    print('-'*100)
    workFlow.run4cluster()
    print('='*100)
    """

    # # get corpus for classification of the event
    # print('='*100)
    # print('Getting corpus for classification of the event ...')
    # print('-'*100)
    # workFlow.getCorpus4Classification(folderpath)
    # print('='*100)

    """
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
    rootpath = "/home/1877/Data/pheme_dataset"

    folders = [folder for folder in os.listdir(
        rootpath) if os.path.isdir(rootpath+"/"+folder)]
    print("="*100)
    print(folders)
    print("="*100)

    event2eps = {"BandyLee_0110_0115": 0.65,
                 "Capriccio_0516_0523_new": 0.5,
                 "Gabapentin_0628_0121": 0.35,
                 "immigrants_0622_0624": 0.3,
                 "Ingraham_0618_0624": 0.5,
                 "ItsJustAJacket_0621_0624": 0.45,
                 "JackBreuer_1228_0115": 0.6,
                 "JetLi_0519_0523": 0.6,
                 "SanctuaryCities_0516_0523": 0.3,
                 "SouthwestKey_0620_0624": 0.45,
                 "WhereAreTheChildren_0418_0527": 0.35,
                 "charliehebdo-all-rnr-threads": 0.5,
                 "ebola-essien-all-rnr-threads": 0.5,
                 "ferguson-all-rnr-threads": 0.5,
                 "germanwings-crash-all-rnr-threads": 0.45,
                 "gurlitt-all-rnr-threads": 0.5,
                 "ottawashooting-all-rnr-threads": 0.5,
                 "prince-toronto-all-rnr-threads": 0.5,
                 "putinmissing-all-rnr-threads": 0.5,
                 "sydneysiege-all-rnr-threads": 0.5,
                 "alfieevans_0301_0315": 0.5,
                 "AnthonyBourdain_0610_0630": 0.5,
                 "CanadianDoctors_0201_0331": 0.5,
                 "dogjealousy_0101_0708": 0.5,
                 "Irma_0830_0910": 0.5,
                 "JoeJackson_0623_0626": 0.5,
                 "pavingforpizza_0612_0706": 0.5,
                 "RobertDeNiro_0611_0613": 0.5,
                 "TrumpKimSummit_0612_0630": 0.5,
                 "TrumpRally_0705_0707": 0.5,
                 "TrumpSalary_0301_0531": 0.5}

    for folder in folders:
        # exclude some events
        # if folder not in ["SouthwestKey_0620_0624", "WhereAreTheChildren_0418_0527"]:
        #     continue

        # specify an event
        # if folder != "germanwings-crash-all-rnr-threads":
        #     continue

        # run total events
        # if folder[0] == ".":
        #     continue

        print("Running code for {}".format(folder))
        args = ['python', 'main.py', '-r', rootpath,
                '-f', folder, '-q', "#"+folder.split("_")[0], '-s', 'test', '-e', 'test', "-p", str(event2eps[folder])]
        # args = ['python', 'main.py']
        print("Command line is {}".format(" ".join(args)))
        # subprocess.call(args)
        # break
        # time.sleep(random.randint(1, 121))
        main(rootpath, folder, "#"+folder.split("_")
             [0], 'test', 'test', eps=event2eps[folder])
