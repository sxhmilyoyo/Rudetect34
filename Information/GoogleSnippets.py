from bs4 import BeautifulSoup
import codecs
import json
import os
import requests
import sys


class GoogleSnippets(object):
    """Get google search snippets."""

    def __init__(self, folderpath, query_id, query):
        """Initialize the parameters.

        Parameters
        ----------
        folderpath : str
            the folder path of the event folder
        query_id : str
            the name of event
        query : str
            the query

        Returns
        -------
        None

        """
        self.folderpath = folderpath
        self.query_id = query_id
        self.query = query
        self.results_limit = 20
        self.pages_cnt = 1
        self.crawl_idx = 1
        self.url_base = ''
        self.parameters = {}
        self.url_list = []
        self.results = []
        self.output_root = os.path.join(self.folderpath, 'snippets')
        self.googletest = os.path.join(self.folderpath, 'googletest')
        if not os.path.exists(self.output_root):
            os.makedirs(self.output_root)
        if not os.path.exists(self.googletest):
            os.makedirs(self.googletest)

    def get_page(self, url, para=None):
        """Get the result pages of google search.

        Parameters
        ----------
        url : str
            the url of the search
        para : dic
            parameters of the url

        Returns
        -------
        str
            url of the response, content of the response
            OR 'ERROR', 'ERROR'

        """
        try:
            response = requests.get(url, params=para)
            # print(response.url)
            response.encoding = 'utf-8'
            if response.status_code == 403:
                print('403 {}'.format(url))
                sys.exit()
            return response.url, response.text
        except Exception:
            print('Error: {}'.format(url))
            return('ERROR', 'ERROR')

    def google_get_search_results(self, url, content):
        """Get the search results of the google.

        Parameters
        ----------
        url : str
            the url of the search
        content : str
            the content of the result

        Returns
        -------
        None
            {'id': self.query_id + '_google_' + str(self.crawl_idx), 'url':
             url, 'snippets': snippets} stored in self.result

        """
        page = BeautifulSoup(content, 'lxml')
        if page.find('div', id='ires'):
            list_results = page.find('div', id='ires').find_all('div', 'g')

            for l in list_results:
                if l.find('h3', 'r'):
                    title = l.find('h3', 'r').get_text()
                    href = l.find('h3', 'r').a['href']
                    decoder = href.split('?')[1].split('&')
                    href_link = ''
                    for d in decoder:
                        # print d
                        if d.split('=')[0] == 'q':
                            href_link = d.split('=')[1]
                            if len(href_link) > 0:
                                url = href_link
                                # avoid the duplicate urls
                                if url not in self.url_list:
                                    self.url_list.append(url)
                                    if l.find('span', 'st'):
                                        snippets = l.find(
                                            'span', 'st').get_text()
                                    else:
                                        snippets = u''

                                    self.results.append(
                                        {
                                            'id': str(self.query_id) +
                                            '_google_' +
                                            str(self.crawl_idx),
                                            'url': url,
                                            'title': title,
                                            'snippets': snippets
                                        }
                                    )

                                    self.crawl_idx += 1
                                    # print self.pages_cnt,self.max_pages
                                    if self.crawl_idx > self.results_limit:
                                        self.crawl_idx = 1
                                        return

            if page.find('table', id='nav'):
                page_index = page.find('table', id='nav').find_all('td')

                # for ele in page_index:
                # print ele

                for i in range(len(page_index)):
                    # the condition that terminate the recursion
                    if not page_index[i].find('a'):
                        if self.pages_cnt == 1:
                            next_page = page_index[i + 2]
                        else:
                            next_page = page_index[i + 1]

                        if next_page.find('a'):
                            next_url = 'http://www.google.com' + \
                                next_page.a['href']
                            self.pages_cnt += 1
                            next_url, next_content = self.get_page(next_url)
                            self.google_get_search_results(
                                next_url, next_content)
                        else:
                            return
                        break

    def google_crawl(self):
        """Combine the get_page() and google_get_search_results().

        Returns
        -------
        None
            save the self.result in the google.json file

        """
        self.url_base = 'http://www.google.com/search?'
        self.parameters = {}
        self.parameters['q'] = self.query
        self.parameters['hl'] = 'en'

        self.pages_cnt = 1
        self.crawl_idx = 1
        self.results = []
        self.url_list = []

        final_url, content = self.get_page(self.url_base, self.parameters)

        with codecs.open(os.path.join(self.googletest, str(self.query_id)
                                      + '_google_test.html'), 'wb', 'utf-8') as out:
            out.write(content)

        print('crawling Google data...')

        self.google_get_search_results(final_url, content)
        with codecs.open(os.path.join(self.output_root, str(self.query_id) +
                                      '_google.json'), 'wb', 'utf-8') as f:
            json.dump(self.results, f, indent=4)
        print("snippets have been saved as {}".format(self.output_root))
        return self.results

    def start_crawl(self):
        """Start crawling.

        Returns
        -------
        None

        """
        # print('Query:' + self.query)
        return self.google_crawl()
