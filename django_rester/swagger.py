from .url_mapper import UrlMapper
from .singleton import Singleton


class SwaggerGenerator(metaclass=Singleton):

    def __init__(self):
        self.url_view_map = UrlMapper().urls_class_map
