from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers

from django_rester.views import BaseAPIView
from .singleton import Singleton


class UrlMapper(metaclass=Singleton):
    urls_class_map = {}

    def __init__(self):
        urls = urlresolvers.get_resolver()
        self._build_map(urls)

    @staticmethod
    def _filter_rester_views(name):
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

    def _build_map(self, urls, parent_pattern=None):
        for url in urls.url_patterns:
            url_pattern = "{}{}".format(parent_pattern or '', url.regex.pattern)
            if isinstance(url, RegexURLResolver):
                self._build_map(url, url_pattern)
            elif isinstance(url, RegexURLPattern):
                _cls = self._filter_rester_views(url.lookup_str)
                if _cls:
                    self.urls_class_map.update({url_pattern: _cls})
