import sys
sys.path.append("..")
import Twitter


def main():
    rootpath = '/local/data/haoxu/Rudetect'
    folderpath = 'Gabapentin_0628_0121'
    start = '2017-06-28'
    end = '2018-01-21'
    originhashtag = '#gabapentin'
    gettweets = Twitter.GetTweets(rootpath, folderpath, start, end, originhashtag)
    gettweets.start_getTweets()

if __name__ == '__main__':
    main()
