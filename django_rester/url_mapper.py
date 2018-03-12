from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers

from django_rester.views import BaseAPIView


class UrlMapper:

    def __init__(self):
        urls = urlresolvers.get_resolver()
        self.urls_class_map = {}
        self._build_map(urls)

    @staticmethod
    def _import_by_path(name):
        _cls = None
        components = name.split('.')
        module = __import__(components[0])
        for comp in components[1:]:
            module = getattr(module, comp)
            try:
                if module.__bases__[0] is BaseAPIView:
                    _cls = module
            except AttributeError:
                continue
        return _cls

    @staticmethod
    def _if_none(value):
        if value:
            return value
        return ''

    def _build_map(self, urls, parent_pattern=None):
        for url in urls.url_patterns:
            url_pattern = "{}{}".format(self._if_none(parent_pattern), url.regex.pattern)
            if isinstance(url, RegexURLResolver):
                self._build_map(url, url_pattern)
            elif isinstance(url, RegexURLPattern):
                _cls = self._import_by_path(url.lookup_str)
                if _cls:
                    self.urls_class_map.update({url_pattern: _cls})
