import pycurl
import logging
import json as json_lib
import urllib.parse as urllib_parse
from urllib.parse import urljoin
from io import BytesIO

from django_rester.exceptions import ResterException

logger = logging.getLogger('django_rester.client')

DEFAULT_OPTIONS = {
    'HTTPHEADER': ['Accept: application/json',
                   'Accept-Charset: UTF-8',
                   'Content-Type: application/json; charset=utf-8'],
    'CONNECTTIMEOUT': 5,
    'TIMEOUT': 8,
    'COOKIEFILE': '',
    'FAILONERROR': 0,
}

'''A high-level interface to the pycurl extension'''


# ** mfx NOTE: the CGI class uses "black magic" using COOKIEFILE in
#    combination with a non-existent file name. See the libcurl docs
#    for more info.


# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.
# try:
#     import signal
#     from signal import SIGPIPE, SIG_IGN
# except ImportError:
#     pass
# else:
#     signal.signal(SIGPIPE, SIG_IGN)


class Curl:
    """High-level interface to pycurl functions."""

    def __init__(self, base_url="", headers=None):
        self.handle = pycurl.Curl()
        # These members might be set.
        self.base_url = ""
        self.set_url(base_url)
        self.verbosity = 0
        self.headers = headers or []
        # Nothing past here should be modified by the caller.
        self.payload = None
        self.payload_io = BytesIO()
        self.hdr = ""
        # Verify that we've got the right site; harmless on a non-SSL connect.
        self.set_option(pycurl.SSL_VERIFYHOST, 2)
        # Follow redirects in case it wants to take us to a CGI...
        self.set_option(pycurl.FOLLOWLOCATION, 1)
        self.set_option(pycurl.MAXREDIRS, 5)
        self.set_option(pycurl.NOSIGNAL, 1)
        # Setting this option with even a nonexistent file makes libcurl
        # handle cookie capture and playback automatically.
        self.set_option(pycurl.COOKIEFILE, "/dev/null")
        # Set timeouts to avoid hanging too long
        self.set_timeout(30)
        # Use password identification from .netrc automatically
        self.set_option(pycurl.NETRC, 1)
        self.set_option(pycurl.WRITEFUNCTION, self.payload_io.write)

        def header_callback(x):
            self.hdr += x.decode('ascii')

        self.set_option(pycurl.HEADERFUNCTION, header_callback)

    def set_timeout(self, timeout):
        """Set timeout for a retrieving an object"""
        self.set_option(pycurl.TIMEOUT, timeout)

    def set_url(self, url):
        """Set the base URL to be retrieved."""
        self.base_url = url
        self.set_option(pycurl.URL, self.base_url)

    def set_option(self, *args):
        """Set an option on the retrieval."""
        self.handle.setopt(*args)

    def set_verbosity(self, level):
        """Set verbosity to 1 to see transactions."""
        self.set_option(pycurl.VERBOSE, level)

    def __request(self, relative_url=None):
        """Perform the pending request."""
        if self.headers:
            self.set_option(pycurl.HTTPHEADER, self.headers)
        if relative_url:
            self.set_option(pycurl.URL, urljoin(self.base_url, relative_url))
        self.payload = None
        self.payload_io.seek(0)
        self.payload_io.truncate()
        self.hdr = ""
        try:
            self.handle.perform()
        except ResterException:
            pass
        self.payload = self.payload_io.getvalue()
        return (self.payload,
                self.handle.getinfo(pycurl.RESPONSE_CODE),
                self.handle.errstr())

    def get(self, url="", params=None):
        """Ship a GET request for a specified URL, capture the response."""
        if params:
            url += "?" + urllib_parse.urlencode(params)
        self.set_option(pycurl.HTTPGET, 1)
        return self.__request(url)

    def post(self, url="", params=None):
        """Ship a POST request to a specified CGI, capture the response."""
        self.set_option(pycurl.POST, 1)
        if params:
            self.set_option(pycurl.POSTFIELDS, urllib_parse.urlencode(params))
        return self.__request(url)

    def body(self):
        """Return the body from the last response."""
        return self.payload

    def header(self):
        """Return the header from the last response."""
        return self.hdr

    def get_info(self, *args):
        """Get information about retrieval."""
        return self.handle.getinfo(*args)

    def info(self):
        """Return a dictionary with all info on the last response."""
        m = {'effective-url': self.handle.getinfo(pycurl.EFFECTIVE_URL),
             'http-code': self.handle.getinfo(pycurl.HTTP_CODE),
             'total-time': self.handle.getinfo(pycurl.TOTAL_TIME),
             'namelookup-time': self.handle.getinfo(pycurl.NAMELOOKUP_TIME),
             'connect-time': self.handle.getinfo(pycurl.CONNECT_TIME),
             'pretransfer-time': self.handle.getinfo(pycurl.PRETRANSFER_TIME),
             'redirect-time': self.handle.getinfo(pycurl.REDIRECT_TIME),
             'redirect-count': self.handle.getinfo(pycurl.REDIRECT_COUNT),
             'size-upload': self.handle.getinfo(pycurl.SIZE_UPLOAD),
             'size-download': self.handle.getinfo(pycurl.SIZE_DOWNLOAD),
             'speed-upload': self.handle.getinfo(pycurl.SPEED_UPLOAD),
             'header-size': self.handle.getinfo(pycurl.HEADER_SIZE),
             'request-size': self.handle.getinfo(pycurl.REQUEST_SIZE),
             'content-length-download': self.handle.getinfo(
                 pycurl.CONTENT_LENGTH_DOWNLOAD),
             'content-length-upload': self.handle.getinfo(
                 pycurl.CONTENT_LENGTH_UPLOAD),
             'content-type': self.handle.getinfo(pycurl.CONTENT_TYPE),
             'response-code': self.handle.getinfo(pycurl.RESPONSE_CODE),
             'speed-download': self.handle.getinfo(pycurl.SPEED_DOWNLOAD),
             'ssl-verifyresult': self.handle.getinfo(pycurl.SSL_VERIFYRESULT),
             'filetime': self.handle.getinfo(pycurl.INFO_FILETIME),
             'starttransfer-time': self.handle.getinfo(
                 pycurl.STARTTRANSFER_TIME),
             'http-connectcode': self.handle.getinfo(pycurl.HTTP_CONNECTCODE),
             'httpauth-avail': self.handle.getinfo(pycurl.HTTPAUTH_AVAIL),
             'proxyauth-avail': self.handle.getinfo(pycurl.PROXYAUTH_AVAIL),
             'os-errno': self.handle.getinfo(pycurl.OS_ERRNO),
             'num-connects': self.handle.getinfo(pycurl.NUM_CONNECTS),
             'ssl-engines': self.handle.getinfo(pycurl.SSL_ENGINES),
             'cookielist': self.handle.getinfo(pycurl.INFO_COOKIELIST),
             'lastsocket': self.handle.getinfo(pycurl.LASTSOCKET),
             'ftp-entry-path': self.handle.getinfo(pycurl.FTP_ENTRY_PATH)}
        return m

    def answered(self, check):
        """Did a given check string occur in the last payload?"""
        return self.payload.find(check) >= 0

    def close(self):
        """Close a session, freeing resources."""
        if self.handle:
            self.handle.close()
        self.handle = None
        self.hdr = ""
        self.payload = ""

    def __del__(self):
        self.close()


class ResterClient(Curl):
    def __init__(self, base_url='', headers=None, opts=None):
        super().__init__(base_url, headers or [])
        all_opts = dict(DEFAULT_OPTIONS)
        all_opts.update(opts or {})
        self.set_options(all_opts)

    def set_options(self, opts):
        for key, value in opts.items():
            opt_key = getattr(pycurl, key.replace('-', '_').upper(), None)
            if opt_key:
                self.set_option(opt_key, value)

    def get(self, url='', params=None):
        response, response_code, msg = super().get(url, params)
        return self._response_decode(response, response_code, msg)

    def post(self, url='', params=None, json=None):
        if json:
            body = json_lib.dumps(json)
            self.set_option(pycurl.POSTFIELDS, body)
        response, response_code, msg = super().post(url, params)
        return self._response_decode(response, response_code, msg)

    @staticmethod
    def _response_decode(response, response_code=200, message=''):
        resp_type = None
        data = None
        if response:
            try:
                data = json_lib.loads(isinstance(response, bytes)
                                      and response.decode('utf-8')
                                      or response)
                resp_type = 'json'
            except json_lib.decoder.JSONDecodeError:
                data = response
                resp_type = 'text'

        return {'type': resp_type,
                'message': message and [message] or [],
                'response_code': response_code,
                'data': data}
