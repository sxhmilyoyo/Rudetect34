from bs4 import BeautifulSoup
import codecs
import os
import requests
import sys
# sys.path.append("..")
# from Helper import Helper
import Utility
import traceback

class GetHashtagPopularity(object):
    """Get the number of results from google search."""

    def __init__(self, query, rootpath, folderpath):
        """Initialize the parameters.

        Parameters
        ----------
        query : str
            the query for google search.

        Returns
        -------
        None

        """
        self.query = query
        self.rootpath = rootpath
        self.folderpath = folderpath
        self.url_base = ''
        self.parameters = {}
        self.helper = Utility.Helper(rootpath)

    def get_page(self, url, para=None):
        """Get page from google based on url.

        Parameters
        ----------
        url : str
            the url of the page.
        para : dic
            the parameters of the url.

        Returns
        -------
        str, str
            response.url: the response url
            response.text: the content

        """
        try:
            response = requests.get(url, params=para)
            print(response.url)
            response.encoding = 'utf-8'
            if response.status_code == 403:
                print('403 ' + url)
                sys.exit()
            return response.text
        except Exception:
            print('Error: ' + url)
            return 'ERROR', 'ERROR'

    def google_get_num_results(self, content):
        """Get the number of the results.

        Parameters
        ----------
        url : str
            the url of the search.
        content : str
            the content of the html.

        Returns
        -------
        int
            the number of results.

        """
        page = BeautifulSoup(content, 'lxml')
        results_cnt = 0
        try:
            if page.find(id='resultStats') and page.find(id='resultStats').text:
                numStr = page.find(id='resultStats').string.split()[-2]
                numStr = ''.join(numStr.split(','))
                results_cnt = int(numStr)
            else:
                print ("{}Error: no resultStats!{}".format('*' * 10, '*' * 10))
        except:
            traceback.print_exc()
        return results_cnt

    def google_crawl(self):
        """Call the get_page() and google_get_num_results().

        Save the {hashtag: num} as the hashtagNum.json.
        Returns
        -------
        None

        """
        self.url_base = 'http://www.google.com/search?'
        self.parameters = {}
        self.parameters['q'] = self.query
        self.parameters['hl'] = 'en'

        hashtag = self.query.split()[0]
        content = self.get_page(self.url_base, self.parameters)

        folderPath = os.path.join(self.folderpath, 'experiment')
        fullPath = os.path.join(self.rootpath, folderPath, 'google_test')
        if os.path.exists(fullPath):
            with codecs.open(os.path.join(fullPath, hashtag + '.html'), 'wb',
                             'utf-8') as out:
                out.write(content)
        else:
            os.makedirs(fullPath)
            with codecs.open(os.path.join(fullPath, hashtag + '.html'), 'wb',
                             'utf-8') as out:
                out.write(content)
        print('crawling Google data...')

        results_cnt = self.google_get_num_results(content)
        if os.path.exists(os.path.join(fullPath, 'hashtagNum.json')):
            hashtagNum = self.helper.loadJson(os.path.join(fullPath,
                                              'hashtagNum.json'))
        else:
            hashtagNum = {}
        hashtagNum[hashtag] = results_cnt
        self.helper.dumpJson(fullPath, 'hashtagNum.json', hashtagNum)

    def start_crawl(self):
        """Start Function.

        Returns
        -------
        None

        """
        print('Query:' + self.query)
        self.google_crawl()
