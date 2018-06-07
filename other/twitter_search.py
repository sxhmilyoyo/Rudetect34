import time
import tweepy
import codecs
import os
import json
from tweepy import OAuthHandler
consumer_key="cxRBdyw5uF8nX0tUAOd7bkPCu"
consumer_secret="Kowz2iCaC4yeF84L5jX0ql5m7SMrssPqh3QxyzEz1jLzPSiHqH"

access_token="724966264419024897-mJeva42j3HAozgjwj2ZMdrSRM7S95kT"
access_token_secret="o265mwSzlwNE4ZZEYRUMw9xRz5qoIAagCNJKf83l72VOw"

auth = OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

# query_hashtag='#haiku' #search with #hashtag
# '#zika'
# query_words='trump since:2016-10-04 until:2016-10-05'

# 180 queries per 15 minute
def tweetApiCrawler(query_words,store_path,max=10000):
    tweets=[]
    count=0
    # index=1
    try:
        for page in tweepy.Cursor(api.search,
                               q=query_words,
                               count=100,
                               result_type="mixed",
                               include_entities=True,
                               lang="en").pages():
            count+=1
            for p in page:
                tweets.append(p._json)

            result=[]
            for tweet in tweets:
                if 'retweeted_status' not in tweet and (tweet['in_reply_to_user_id']==None) :
                # if 'retweeted_status' not in tweet and (tweet['in_reply_to_user_id']==None or tweet['in_reply_to_status_id']!=None) :
                    result.append(tweet)
            print len(result)
            if len(result)>=max:
                break
            #     with codecs.open(store_path+'_'+str(index)+'.json', 'a', 'utf-8') as f:
            #         json.dump(tweets, f, indent=4)
            #     index+=1
            # tweets=[]
            time.sleep(5)
        with codecs.open(store_path+'.json', 'w', 'utf-8') as f:
                json.dump(result, f, indent=4)
        return result
    except Exception,e:
        print e
        pass

# a  for appending
if __name__ == '__main__':
    query='wodemingzijiaowangye wangye'
    path='data/'
    count=len(tweetApiCrawler(query,path+query+'_api',100000000))
    print "MAX_API_COUNT:",count