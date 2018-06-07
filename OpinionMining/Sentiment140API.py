import json
import requests
import Utility


class Sentiment140API(object):
    """Wrap the sentiment140 api."""

    def __init__(self, appid=None, per_bulk_request=5000):
        """Initialize the parameters.

        Parameters
        ----------
        appid : str
            the registered email
        per_bulk_request : int
            the size of the bulk

        Returns
        -------
        None

        """
        self.helper = Utility.Helper('/local/data/haoxu/Rudetect')
        self.BASE_URL = "http://www.sentiment140.com/api"
        self.appid = 'xh19920904@icloud.com'
        self.per_bulk_request = per_bulk_request

    def _build_url(self, api_method):
        return '/'.join([self.BASE_URL, api_method])

    def _fetch_url(self, url, data=None, params=None, method='GET'):
        if params is None:
            params = {}

        # if self.appid:
        #     params['appid'] = self.appid
        url = url+'?appid='+self.appid

        return requests.request(method=method, url=url,
                                data=data, params=params)

    def classify(self, text):
        """Classify the single text.

        Parameters
        ----------
        text : str
            the single text

        Returns
        -------
        type
            the sentiment result

        """
        url = self._build_url('classify')
        return self._fetch_url(url, params={'text': text}).json()['results']

    def bulk_classify_json(self, data):
        """Classify the bulk of text.

        Parameters
        ----------
        data : list
            [
                {'text': ..., 'id': ..., 'query': ..., 'topic': ...},
                {'text': ..., 'id': ..., 'query': ..., 'topic': ...},
                ...
            ]

        Returns
        -------
        list
            [
                {"text": ..., "id": ..., "polarity": ...},
                {"text": ..., "id": ..., "polarity": ...}
            ]

        """
        results = []

        for chunk in self.helper.chunkify(data, self.per_bulk_request):
            url = self._build_url('bulkClassifyJson')

            results.extend(self._fetch_url(url, data=json.dumps(
                           {'data': data}), method='POST').json()['data'])

        return results
