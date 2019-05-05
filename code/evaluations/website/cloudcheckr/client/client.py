import httplib2
import json
import urllib

from endpoints import endpoints


class CloudCheckr(object):
    def __init__(self, access_key, hostname='https://api.cloudcheckr.com/api', headers=None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        self.hostname = hostname.rstrip('/')
        self.access_key = access_key
        self.endpoints = endpoints
        self.headers = headers

    def __getattr__(self, method):
        def callback(self, **kwargs):
            endpoint = self.endpoints[method]

            verb = endpoint['method']
            url = self.hostname + endpoint['path'] + '?access_key=' + self.access_key
            for kw in kwargs:
                if kw not in endpoint['params']:
                    raise ValueError(
                        'Keyword argument(s) not valid. Valid arguments are: %s' %
                        ', '.join(endpoint['params']))
                else:
                    url += '&' + urllib.urlencode(kwargs)
            self.client = httplib2.Http('.cache',
                                            disable_ssl_certificate_validation=True)
            (response, content) = self.client.request(url,
                                                    verb,
                                                    body=None,
                                                    headers=self.headers)
            return json.loads(content)
        if method not in self.endpoints:
          raise AttributeError('%s() method does not exist.' % method)
        return callback.__get__(self)
