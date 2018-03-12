from .url_mapper import UrlMapper

class SwaggerGenerator:

    def __init__(self):
        self.url_view_map = UrlMapper().urls_class_map