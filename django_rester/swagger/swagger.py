import json

from django.conf import settings
from django_rester.fields import SwaggerFields
from django_rester.singleton import Singleton
from django_rester.swagger.url_map import UrlMap
from django_rester.swagger.settings import rester_swagger_settings


class SwaggerGenerator(metaclass=Singleton):
    make_swagger_file = getattr(settings, 'DJANGO_RESTER_SWAGGER', False)
    swagger_title = rester_swagger_settings['INFO']

    def __init__(self, url_map=None):
        self.url_map = url_map or UrlMap()
        self.title_data = self.check_json_data(self.swagger_title)

    @staticmethod
    def check_json_data(data):
        return json.loads(json.dumps(data))

    def generate_json_structure(self):
        paths = {}
        for url, view in self.url_map.items():
            path = {url: self.generate_data_for_view(view)}
            paths.update(path)

        return paths

    def generate_data_for_view(self, view):
        base_structure = {}
        # if not view.swagger_fields:
        #    base_structure = None
        if isinstance(view.swagger_fields, dict):
            for method, swagger_fields in view.swagger_fields.items():
                base_structure = {method: {k: v for k, v in swagger_fields.__dict__.items()}}

        return base_structure
