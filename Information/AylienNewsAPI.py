import aylien_news_api
from aylien_news_api.rest import ApiException
import time


class AylienNewsAPI(object):
    """Get news from ALYEN NewsAPI."""

    def __init__(self):
        # ÷ Configure API key authorization: app_id
        aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = 'af9d3b70'
        # Configure API key authorization: app_key
        aylien_news_api.configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = '3eeceb408f60f77d7719509bf902c09e'
        self.api_instance = aylien_news_api.DefaultApi()

        self.opts = {
            'text': '',
            'sort_by': 'relevance',
            'language': ['en'],
            'published_at_start': '',
            'published_at_end': '',
            '_return': ['id', 'title', 'body', 'summary', 'sentiment', 'links']
        }

    def getNews(self, query, start, end, total):
        self.opts['text'] = query
        self.opts['published_at_start'] = start
        self.opts['published_at_end'] = end
        self.opts['per_page'] = total

        flag = True
        news = []

        while flag:
            try:
                api_response = self.api_instance.list_stories_with_http_info(
                    **self.opts)
                x_ratelimit_limit = api_response[2]['X-RateLimit-Limit']
                x_ratelimit_remaining = api_response[2]['X-RateLimit-Remaining']
                x_ratelimit_reset = api_response[2]['X-RateLimit-Reset']
                if int(x_ratelimit_remaining) == 0:
                    flag = True
                    print('API called successfully. Rate limit headers are as follows:')
                    print("X-RateLimit-Limit: %s" %
                          api_response[2]['X-RateLimit-Limit'])
                    print("X-RateLimit-Remaining: %s" %
                          api_response[2]['X-RateLimit-Remaining'])
                    print("X-RateLimit-Reset: %s" %
                          api_response[2]['X-RateLimit-Reset'])
                    interval = time.time() - \
                        int(api_response[2]['X-RateLimit-Reset'])
                    print("waiting {}...".format(interval))
                    time.sleep(interval)
                else:
                    flag = False
                    print("API called successfully. Returned data: ")
                    print("="*60)
                    for story in api_response[0].stories:
                        news.append(story)
                        print(story.title)
            except ApiException as e:
                print("Exception when calling DefaultApi->list_stories: %sn" % e)
        return news

    def getTitles(self, news):
        titles = []
        for new in news:
            titles.append(new.title)
        return titles

    def getSentiment(self, news):
        sentiments = []
        for new in news:
            sentiment = new.sentiment
            titleSentiment = sentiment.title.polarity
            bodySentiment = sentiment.body.polarity
            if titleSentiment == bodySentiment:
                sentiments.append("FAVOR")
            elif titleSentiment != bodySentiment:
                sentiments.append("AGAINST")
        return sentiments
