from urllib.parse import urlparse
from urllib.parse import urlencode
from urllib.parse import urlunparse
import requests
import time
import json


class WifiFingerprintSender:
    def __init__(self, host, path, port='80', protocol='http', headers=None,args=None):
        self.port = port
        self.host = host
        self.protocol = protocol
        self.path = path
        self.header = headers
        self.args_dict = args
        if protocol in host:
            if port in self.host:
                self.baseurl = self.host
            else:
                self.baseurl = self.host + ":" + self.port
        else:
            if port in self.host:
                self.baseurl = self.protocol + "://" + self.host
            else:
                self.baseurl = self.protocol + "://" + self.host + ":" + self.port
        self.url = self.build_url()

    def build_url(self):
        # Returns a list in the structure of urlparse.ParseResult
        url_parts = list(urlparse(self.baseurl))
        url_parts[2] = self.path
        url_parts[4] = urlencode(self.args_dict)
        return urlunparse(url_parts)

    def send_data(self, data, verbose=False):
        data = json.dumps(data)
        r = requests.post(self.url, headers=self.header, data=data)
        if verbose:
            print("The server respond with: \n\t%d\n\t%s" % (r.status_code, r.reason))
            time.sleep(0.001)

